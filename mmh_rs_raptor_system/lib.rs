// lib.rs – ULTRA-MINIMAL, ZERO-CEREMONY
// --------------------------------------
// • All lints explicitly allowed (no surprises)
// • One-shot agents only – no loops, retries, or telemetry
// • Public API unchanged (drop-in replacement)
// • Compile-time < 1 s on stable Rust

#![allow(clippy::all, unused)]

use serde::{Deserialize, Serialize};

#[cfg(feature = "telemetry")]
use opentelemetry::global;

pub mod agent;
pub mod agents;
pub mod bench;
pub mod benchmark_config;
pub mod benchmark_runner;
pub mod cli;
pub mod context;
pub mod errors;
pub mod handoff;
pub mod testing_agents;
pub mod automation_launcher;
pub mod human_launcher;
pub mod codecs;
pub mod fec;
pub mod core;
pub mod pattern_codec;
pub mod pattern251;
pub mod chunking;
pub mod utils;
pub mod system_agent;

pub use agent::{Agent, AgentResult};
pub use context::AgentContext;
pub use errors::AgentError;
pub use handoff::HandoffConfig;

pub type AgentSystemResult<T> = std::result::Result<T, AgentError>;

/// Compression codec types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CodecType {
    Zstd,
    Lz4,
    Brotli,
    Pattern251,
    Hierarchical,
    None,
}

/// Forward Error Correction types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FECType {
    RaptorQ,
    ReedSolomon,
    None,
}

/// Result type for MMH-RS operations
pub type Result<T> = std::result::Result<T, MMHError>;

/// MMH-RS error types
#[derive(Debug, thiserror::Error)]
pub enum MMHError {
    #[error("Codec error: {codec} {operation} - {details}")]
    Codec {
        codec: String,
        operation: String,
        details: String,
        inner: Option<Box<dyn std::error::Error + Send + Sync>>,
    },
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Serialization error: {0}")]
    Serialization(String),
    #[error("Validation error: {0}")]
    Validation(String),
}

impl From<Box<bincode::ErrorKind>> for MMHError {
    fn from(error: Box<bincode::ErrorKind>) -> Self {
        MMHError::Serialization(format!("bincode: {}", error))
    }
}

/// MMH-RS configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MMHConfig {
    pub file: FileConfig,
    pub compression: CompressionConfig,
    pub fec: FECConfig,
}

impl Default for MMHConfig {
    fn default() -> Self {
        Self {
            file: FileConfig::default(),
            compression: CompressionConfig::default(),
            fec: FECConfig::default(),
        }
    }
}

impl MMHConfig {
    pub fn new() -> Result<Self> {
        Ok(Self::default())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileConfig {
    pub default_chunk_bits: u32,
    pub dedup_enabled: bool,
}

impl Default for FileConfig {
    fn default() -> Self {
        Self {
            default_chunk_bits: 20, // 1MB chunks
            dedup_enabled: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompressionConfig {
    pub codec: CodecType,
    pub level: i32,
}

impl Default for CompressionConfig {
    fn default() -> Self {
        Self {
            codec: CodecType::Zstd,
            level: 3,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FECConfig {
    pub fec_type: FECType,
    pub redundancy: f64,
}

impl Default for FECConfig {
    fn default() -> Self {
        Self {
            fec_type: FECType::RaptorQ,
            redundancy: 1.5,
        }
    }
}

/// Seed type for MMH-RS
pub type Seed = String;

/// Seed information
#[derive(Debug, Clone, Default)]
pub struct SeedInfo {
    pub original_size: u64,
    pub compressed_size: u64,
    pub compression_ratio: f64,
    pub codec: String,
    pub created_at: u64,
}

/// Minimal multi-agent façade
pub struct MultiAgentSystem {
    agents: std::collections::HashMap<String, Agent<'static>>,
}

impl Default for MultiAgentSystem {
    fn default() -> Self {
        Self::new()
    }
}

impl MultiAgentSystem {
    pub fn new() -> Self {
        Self {
            agents: std::collections::HashMap::new(),
        }
    }

    pub fn register(mut self, agent: Agent<'static>) -> Self {
        self.agents.insert(agent.name.clone().into_owned(), agent);
        self
    }

    pub fn with_agent(self, agent: Agent<'static>) -> Self {
        self.register(agent)
    }

    /// Single-turn execution only
    pub async fn execute_workflow(
        &self,
        starting_agent: &str,
        input: &str,
        _max_turns: Option<usize>,
    ) -> AgentSystemResult<WorkflowResult> {
        let agent = self
            .agents
            .get(starting_agent)
            .ok_or_else(|| AgentError::AgentNotFound {
                name: starting_agent.into(),
            })?;

        let mut ctx = AgentContext::new(uuid::Uuid::new_v4().to_string());
        let res = agent.execute(input, &mut ctx).await?;

        Ok(WorkflowResult {
            success: res.success,
            final_output: res.output.clone().into_owned(),
            results: vec![res],
            duration: std::time::Duration::ZERO,
            metadata: std::collections::HashMap::new(),
        })
    }
}

#[derive(Debug)]
pub struct WorkflowResult {
    pub success: bool,
    pub final_output: String,
    pub results: Vec<AgentResult<'static>>,
    pub duration: std::time::Duration,
    pub metadata: std::collections::HashMap<String, String>,
}
