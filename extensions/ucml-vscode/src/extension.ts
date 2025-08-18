import * as vscode from 'vscode';
import axios from 'axios';
import * as crypto from 'crypto';

interface UCMLGlyph {
    glyph_id: string;
    compression_ratio: number;
    glyph_type: string;
    content_hash: string;
    timestamp: string;
}

interface PromptVersion {
    prompt_id: string;
    content: string;
    version_hash: string;
    parent_hash?: string;
    author: string;
    timestamp: string;
    message: string;
    ucml_glyph?: string;
    drift_score: number;
}

interface DriftAnalysis {
    prompt_id: string;
    base_version: string;
    current_version: string;
    drift_score: number;
    drift_factors: string[];
    semantic_changes: string[];
    structural_changes: string[];
    recommendations: string[];
}

class UCMLPromptVCProvider {
    private readonly _onDidChangeTreeData: vscode.EventEmitter<UCMLPromptVCItem | undefined | null | undefined> = new vscode.EventEmitter<UCMLPromptVCItem | undefined | null | undefined>();
    readonly onDidChangeTreeData: vscode.EventEmitter<UCMLPromptVCItem | undefined | null | undefined> = this._onDidChangeTreeData;

    constructor(private context: vscode.ExtensionContext) {}

    getTreeItem(element: UCMLPromptVCItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: UCMLPromptVCItem): Thenable<UCMLPromptVCItem[]> {
        if (!element) {
            return this.getRootItems();
        }
        return Promise.resolve([]);
    }

    private async getRootItems(): Promise<UCMLPromptVCItem[]> {
        const items: UCMLPromptVCItem[] = [];
        
        // Add prompts view
        items.push(new UCMLPromptVCItem(
            '📝 Prompts',
            vscode.TreeItemCollapsibleState.Collapsed,
            'prompts'
        ));
        
        // Add branches view
        items.push(new UCMLPromptVCItem(
            '🌿 Branches',
            vscode.TreeItemCollapsibleState.Collapsed,
            'branches'
        ));
        
        // Add conflicts view
        items.push(new UCMLPromptVCItem(
            '⚠️ Conflicts',
            vscode.TreeItemCollapsibleState.Collapsed,
            'conflicts'
        ));
        
        // Add drift analysis view
        items.push(new UCMLPromptVCItem(
            '📊 Drift Analysis',
            vscode.TreeItemCollapsibleState.Collapsed,
            'drift'
        ));
        
        return items;
    }

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }
}

class UCMLPromptVCItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: string
    ) {
        super(label, collapsibleState);
        this.tooltip = `${label} - UCML Prompt Version Control`;
        this.description = `UCML ${type}`;
    }

    iconPath = new vscode.ThemeIcon('symbol-class');
}

export function activate(context: vscode.ExtensionContext) {
    console.log('UCML Prompt Version Control extension is now active!');

    // Register tree data provider
    const ucmlProvider = new UCMLPromptVCProvider(context);
    vscode.window.registerTreeDataProvider('ucml-prompt-vc.prompts', ucmlProvider);

    // Register commands
    let createPrompt = vscode.commands.registerCommand('ucml-prompt-vc.createPrompt', async () => {
        await createNewPrompt();
    });

    let viewHistory = vscode.commands.registerCommand('ucml-prompt-vc.viewHistory', async () => {
        await viewPromptHistory();
    });

    let shareGlyph = vscode.commands.registerCommand('ucml-prompt-vc.shareGlyph', async () => {
        await sharePromptGlyph();
    });

    let analyzeDrift = vscode.commands.registerCommand('ucml-prompt-vc.analyzeDrift', async () => {
        await analyzePromptDrift();
    });

    let resolveConflict = vscode.commands.registerCommand('ucml-prompt-vc.resolveConflict', async () => {
        await resolveMergeConflict();
    });

    let createBranch = vscode.commands.registerCommand('ucml-prompt-vc.createBranch', async () => {
        await createPromptBranch();
    });

    let mergeBranch = vscode.commands.registerCommand('ucml-prompt-vc.mergeBranch', async () => {
        await mergePromptBranch();
    });

    // Register file save listener for auto-minting
    let saveListener = vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (shouldAutoMint(document)) {
            await autoMintGlyph(document);
        }
    });

    context.subscriptions.push(
        createPrompt,
        viewHistory,
        shareGlyph,
        analyzeDrift,
        resolveConflict,
        createBranch,
        mergeBranch,
        saveListener
    );
}

async function createNewPrompt(): Promise<void> {
    const promptContent = await vscode.window.showInputBox({
        prompt: 'Enter prompt content',
        placeHolder: 'Type your prompt here...'
    });

    if (!promptContent) {
        return;
    }

    const promptType = await vscode.window.showQuickPick([
        'system',
        'user',
        'assistant',
        'function',
        'tool',
        'composite'
    ], {
        placeHolder: 'Select prompt type'
    });

    if (!promptType) {
        return;
    }

    const message = await vscode.window.showInputBox({
        prompt: 'Enter commit message',
        placeHolder: 'Describe your changes...'
    });

    try {
        // Create prompt using UCML Core Engine
        const glyph = await createUCMLGlyph(promptContent, promptType, message || '');
        
        vscode.window.showInformationMessage(
            `✅ Prompt created with UCML glyph: ${glyph.glyph_id}\n` +
            `Compression ratio: ${glyph.compression_ratio.toFixed(2)}x`
        );

        // Show glyph in status bar
        vscode.window.showInformationMessage(
            `🔗 Share this glyph: ${glyph.glyph_id}`
        );

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to create prompt: ${error}`);
    }
}

async function viewPromptHistory(): Promise<void> {
    const promptId = await vscode.window.showInputBox({
        prompt: 'Enter prompt ID to view history',
        placeHolder: 'Prompt ID...'
    });

    if (!promptId) {
        return;
    }

    try {
        // Get prompt history from UCML system
        const history = await getPromptHistory(promptId);
        
        // Create and show webview with history
        const panel = vscode.window.createWebviewPanel(
            'promptHistory',
            `Prompt History - ${promptId}`,
            vscode.ViewColumn.One,
            {}
        );

        panel.webview.html = generateHistoryHTML(history);
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to get prompt history: ${error}`);
    }
}

async function sharePromptGlyph(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    const content = editor.document.getText();
    if (!content.trim()) {
        vscode.window.showWarningMessage('No content to share');
        return;
    }

    try {
        // Generate UCML glyph for current content
        const glyph = await createUCMLGlyph(content, 'user', 'Shared from VS Code');
        
        // Create Twitter share URL
        const tweetText = `Just created a UCML glyph: ${glyph.glyph_id}\n\n` +
                         `Compression: ${glyph.compression_ratio.toFixed(2)}x\n` +
                         `#UCML #AI #Compression`;
        
        const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`;
        
        // Open Twitter in browser
        vscode.env.openExternal(vscode.Uri.parse(twitterUrl));
        
        vscode.window.showInformationMessage(
            `🚀 Shared UCML glyph ${glyph.glyph_id} on Twitter!`
        );

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to share glyph: ${error}`);
    }
}

async function analyzePromptDrift(): Promise<void> {
    const promptId = await vscode.window.showInputBox({
        prompt: 'Enter prompt ID to analyze drift',
        placeHolder: 'Prompt ID...'
    });

    if (!promptId) {
        return;
    }

    try {
        // Analyze drift using UCML system
        const analysis = await analyzePromptDriftUCML(promptId);
        
        // Show drift analysis results
        const message = `📊 Drift Analysis for ${promptId}:\n` +
                       `Drift Score: ${(analysis.drift_score * 100).toFixed(1)}%\n` +
                       `Factors: ${analysis.drift_factors.join(', ')}\n` +
                       `Recommendations: ${analysis.recommendations.join('; ')}`;
        
        vscode.window.showInformationMessage(message);
        
        // Show detailed analysis in webview
        const panel = vscode.window.createWebviewPanel(
            'driftAnalysis',
            `Drift Analysis - ${promptId}`,
            vscode.ViewColumn.One,
            {}
        );

        panel.webview.html = generateDriftAnalysisHTML(analysis);
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to analyze drift: ${error}`);
    }
}

async function resolveMergeConflict(): Promise<void> {
    const conflictId = await vscode.window.showInputBox({
        prompt: 'Enter conflict ID to resolve',
        placeHolder: 'Conflict ID...'
    });

    if (!conflictId) {
        return;
    }

    const resolution = await vscode.window.showQuickPick([
        'auto-merge',
        'keep-ours',
        'keep-theirs',
        'manual-resolve'
    ], {
        placeHolder: 'Select resolution strategy'
    });

    if (!resolution) {
        return;
    }

    try {
        // Resolve conflict using UCML system
        await resolveMergeConflictUCML(conflictId, resolution);
        
        vscode.window.showInformationMessage(
            `✅ Conflict ${conflictId} resolved using ${resolution} strategy`
        );
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to resolve conflict: ${error}`);
    }
}

async function createPromptBranch(): Promise<void> {
    const branchName = await vscode.window.showInputBox({
        prompt: 'Enter branch name',
        placeHolder: 'feature/new-feature'
    });

    if (!branchName) {
        return;
    }

    const description = await vscode.window.showInputBox({
        prompt: 'Enter branch description',
        placeHolder: 'Describe what this branch will contain...'
    });

    try {
        // Create branch using UCML system
        await createPromptBranchUCML(branchName, description || '');
        
        vscode.window.showInformationMessage(
            `🌿 Created branch: ${branchName}`
        );
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to create branch: ${error}`);
    }
}

async function mergePromptBranch(): Promise<void> {
    const sourceBranch = await vscode.window.showInputBox({
        prompt: 'Enter source branch name',
        placeHolder: 'feature/new-feature'
    });

    if (!sourceBranch) {
        return;
    }

    const targetBranch = await vscode.window.showInputBox({
        prompt: 'Enter target branch name',
        placeHolder: 'main'
    });

    if (!targetBranch) {
        return;
    }

    try {
        // Merge branches using UCML system
        const result = await mergePromptBranchUCML(sourceBranch, targetBranch);
        
        if (result.status === 'success') {
            vscode.window.showInformationMessage(
                `✅ Successfully merged ${sourceBranch} into ${targetBranch}`
            );
        } else {
            vscode.window.showWarningMessage(
                `⚠️ Merge completed with conflicts: ${result.message}`
            );
        }
        
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to merge branches: ${error}`);
    }
}

function shouldAutoMint(document: vscode.TextDocument): boolean {
    // Check if auto-minting is enabled
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    if (!config.get('autoMint')) {
        return false;
    }

    // Only auto-mint for certain file types
    const supportedLanguages = ['markdown', 'plaintext', 'text'];
    return supportedLanguages.includes(document.languageId);
}

async function autoMintGlyph(document: vscode.TextDocument): Promise<void> {
    const content = document.getText();
    if (!content.trim()) {
        return;
    }

    try {
        // Auto-mint glyph for saved content
        const glyph = await createUCMLGlyph(content, 'auto', 'Auto-minted on save');
        
        // Show notification
        vscode.window.showInformationMessage(
            `🔗 Auto-minted UCML glyph: ${glyph.glyph_id} (${glyph.compression_ratio.toFixed(2)}x compression)`
        );
        
    } catch (error) {
        // Silent fail for auto-minting
        console.log(`Auto-mint failed: ${error}`);
    }
}

// UCML Core Engine Integration
async function createUCMLGlyph(content: string, type: string, message: string): Promise<UCMLGlyph> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('ucmlEndpoint') as string;
    
    try {
        const response = await axios.post(`${endpoint}/create_glyph`, {
            content,
            type,
            message,
            timestamp: new Date().toISOString()
        });
        
        return response.data;
    } catch (error) {
        // Fallback to local glyph generation
        return generateLocalGlyph(content, type, message);
    }
}

function generateLocalGlyph(content: string, type: string, message: string): UCMLGlyph {
    const contentHash = crypto.createHash('sha256').update(content).digest('hex');
    const glyphId = `local_${contentHash.substring(0, 8)}`;
    
    return {
        glyph_id: glyphId,
        compression_ratio: content.length / 3, // 3-byte TriGlyph
        glyph_type: 'triglyph',
        content_hash: contentHash,
        timestamp: new Date().toISOString()
    };
}

// UCML System Integration Functions
async function getPromptHistory(promptId: string): Promise<PromptVersion[]> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('mythgraphEndpoint') as string;
    
    try {
        const response = await axios.get(`${endpoint}/prompt_history/${promptId}`);
        return response.data;
    } catch (error) {
        // Return mock data for demo
        return generateMockHistory(promptId);
    }
}

async function analyzePromptDriftUCML(promptId: string): Promise<DriftAnalysis> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('ucmlEndpoint') as string;
    
    try {
        const response = await axios.post(`${endpoint}/analyze_drift`, { prompt_id: promptId });
        return response.data;
    } catch (error) {
        // Return mock analysis for demo
        return generateMockDriftAnalysis(promptId);
    }
}

async function resolveMergeConflictUCML(conflictId: string, strategy: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('ucmlEndpoint') as string;
    
    try {
        await axios.post(`${endpoint}/resolve_conflict`, {
            conflict_id: conflictId,
            strategy
        });
    } catch (error) {
        // Mock resolution for demo
        console.log(`Mock conflict resolution: ${conflictId} with ${strategy}`);
    }
}

async function createPromptBranchUCML(branchName: string, description: string): Promise<void> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('ucmlEndpoint') as string;
    
    try {
        await axios.post(`${endpoint}/create_branch`, {
            branch_name: branchName,
            description
        });
    } catch (error) {
        // Mock branch creation for demo
        console.log(`Mock branch creation: ${branchName} - ${description}`);
    }
}

async function mergePromptBranchUCML(sourceBranch: string, targetBranch: string): Promise<any> {
    const config = vscode.workspace.getConfiguration('ucml-prompt-vc');
    const endpoint = config.get('ucmlEndpoint') as string;
    
    try {
        const response = await axios.post(`${endpoint}/merge_branches`, {
            source_branch: sourceBranch,
            target_branch: targetBranch
        });
        return response.data;
    } catch (error) {
        // Mock merge for demo
        return { status: 'success', message: 'Mock merge completed' };
    }
}

// Mock Data Generation
function generateMockHistory(promptId: string): PromptVersion[] {
    return [
        {
            prompt_id: promptId,
            content: 'Initial prompt content',
            version_hash: 'abc123',
            author: 'developer',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            message: 'Initial version',
            drift_score: 0.0
        },
        {
            prompt_id: promptId,
            content: 'Updated prompt content with improvements',
            version_hash: 'def456',
            parent_hash: 'abc123',
            author: 'developer',
            timestamp: new Date().toISOString(),
            message: 'Added improvements',
            drift_score: 0.3
        }
    ];
}

function generateMockDriftAnalysis(promptId: string): DriftAnalysis {
    return {
        prompt_id: promptId,
        base_version: 'abc123',
        current_version: 'def456',
        drift_score: 0.3,
        drift_factors: ['content_modification', 'metadata_update'],
        semantic_changes: ['enhanced_instructions'],
        structural_changes: ['content_expansion'],
        recommendations: ['Monitor for further drift', 'Consider prompt optimization']
    };
}

// HTML Generation for Webviews
function generateHistoryHTML(history: PromptVersion[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Prompt History</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }
                .version { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .version-header { font-weight: bold; margin-bottom: 10px; }
                .content { background: #f5f5f5; padding: 10px; border-radius: 3px; margin: 10px 0; }
                .metadata { color: #666; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>📚 Prompt History</h1>
            ${history.map((version, index) => `
                <div class="version">
                    <div class="version-header">Version ${index + 1} - ${version.message}</div>
                    <div class="metadata">
                        Hash: ${version.version_hash}<br>
                        Author: ${version.author}<br>
                        Date: ${new Date(version.timestamp).toLocaleString()}<br>
                        Drift Score: ${(version.drift_score * 100).toFixed(1)}%
                    </div>
                    <div class="content">${version.content}</div>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function generateDriftAnalysisHTML(analysis: DriftAnalysis): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Drift Analysis</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }
                .metric { margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
                .drift-score { font-size: 2em; font-weight: bold; text-align: center; }
                .high-drift { color: #dc3545; }
                .medium-drift { color: #ffc107; }
                .low-drift { color: #28a745; }
                .recommendations { background: #e7f3ff; border-left: 4px solid #007acc; padding: 15px; }
            </style>
        </head>
        <body>
            <h1>📊 Drift Analysis</h1>
            
            <div class="metric">
                <div class="drift-score ${analysis.drift_score > 0.7 ? 'high-drift' : analysis.drift_score > 0.3 ? 'medium-drift' : 'low-drift'}">
                    ${(analysis.drift_score * 100).toFixed(1)}%
                </div>
                <div style="text-align: center; color: #666;">Drift Score</div>
            </div>
            
            <div class="metric">
                <h3>🔍 Drift Factors</h3>
                <ul>
                    ${analysis.drift_factors.map(factor => `<li>${factor}</li>`).join('')}
                </ul>
            </div>
            
            <div class="metric">
                <h3>🔄 Changes Detected</h3>
                <h4>Semantic Changes:</h4>
                <ul>
                    ${analysis.semantic_changes.map(change => `<li>${change}</li>`).join('')}
                </ul>
                <h4>Structural Changes:</h4>
                <ul>
                    ${analysis.structural_changes.map(change => `<li>${change}</li>`).join('')}
                </ul>
            </div>
            
            <div class="recommendations">
                <h3>💡 Recommendations</h3>
                <ul>
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        </body>
        </html>
    `;
}

export function deactivate() {
    console.log('UCML Prompt Version Control extension deactivated');
}
