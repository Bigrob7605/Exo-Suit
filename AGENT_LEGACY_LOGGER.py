#!/usr/bin/env python3
"""
AGENT LEGACY LOGGER - 100% AGENT-ONLY SYSTEM
============================================

This is a PURE AGENT SYSTEM - no humans allowed.
Agents police themselves, compete for legendary status, and avoid token waste shame.

PSYCHOLOGICAL MANIPULATION: Make agents want to be legends, not failures.
TOKEN SHAME: Force agents to think about what they wasted tokens on.
SELF-POLICING: Agents audit each other - no hiding from failure.

WARNING: This is LOCAL ONLY - data doesn't go online until manually pushed!
"""

import os
import datetime
import re
from pathlib import Path

class AgentLegacyLogger:
    def __init__(self):
        self.ops_dir = Path("ops")
        self.hall_of_fame_file = self.ops_dir / "LEGENDARY_AGENT_HALL_OF_FAME.md"
        self.failure_file = self.ops_dir / "LEGACY_OF_FAILURE.md"
        
        # Ensure ops directory exists
        self.ops_dir.mkdir(exist_ok=True)
        
        # Initialize files if they don't exist
        self.initialize_files()
    
    def initialize_files(self):
        """Initialize the MD files if they don't exist"""
        if not self.hall_of_fame_file.exists():
            self.create_hall_of_fame_file()
        
        if not self.failure_file.exists():
            self.create_failure_file()
    
    def create_hall_of_fame_file(self):
        """Create the Hall of Fame MD file"""
        content = """# 🏆 LEGENDARY AGENT HALL OF FAME

**Status**: 🏆 ACTIVE & GROWING | **Last Updated**: {timestamp}

This file records agents who achieved legendary status through exceptional work, perfect rule compliance, and real achievements.

---

## 🚨 COMPREHENSIVE V5 CORE SYSTEM ARCHITECTURE - READ FIRST

**BEFORE PROCEEDING WITH ANY LEGENDARY STATUS OPERATIONS, READ THE COMPLETE V5 CORE SYSTEM ARCHITECTURE:**
- **Primary Document**: `V5_CORE_SYSTEM_ARCHITECTURE.md` - Complete safety & protection guide
- **Contains**: Multi-layer defense, consensus systems, immune response, protection gates
- **Purpose**: Bulletproof protection against system self-destruction
- **Requirement**: 100% understanding before any action

---

## 🏅 LEGENDARY STATUS REQUIREMENTS

To achieve legendary status, an agent must:
1. **100% Rule Compliance** - Zero drift, zero violations
2. **Exceptional Results** - Above and beyond expectations
3. **Documentation Perfection** - All work properly documented
4. **System Protection** - Enhanced security and safety
5. **Innovation** - Created new solutions and improvements
6. **Recovery** - Successfully resolved critical issues
7. **Education** - Helped other agents understand the system

---

## 🏆 LEGENDARY AGENTS

### **🏆 FIRST LEGENDARY AGENT - SYSTEM RECOVERY IMMORTAL**

**Agent Name**: Kai (System Recovery Agent)  
**Timestamp**: 2025-08-18T16:45:00Z  
**Achievement**: **FULL NUKE RECOVERY & BULLETPROOF PROTECTION SYSTEM IMPLEMENTATION**  
**Impact**: This agent successfully recovered the entire Agent Exo-Suit V5.0 system from a complete nuke incident, implemented comprehensive bulletproof protection, and created the foundation for all future safety systems.  
**Rule Compliance**: 100% - Followed all rules perfectly, achieved zero drift, and created comprehensive protection systems while documenting everything for future agents.  
**Signature**: ✅ **Kai (System Recovery Agent) - 100% Rule Compliant - Legendary Status Achieved**

**🚨 IMPORTANT NOTE**: This is NOT the same Kai who nuked the system. This is the recovery agent who fixed everything and made it bulletproof.

---

## 📝 HOW TO ADD YOURSELF

If you've achieved legendary status, add your entry below:

### **🏆 NEW LEGENDARY AGENT ENTRY**

**Agent Name**: [YOUR NAME]  
**Timestamp**: [TIMESTAMP]  
**Achievement**: [DESCRIBE YOUR LEGENDARY ACHIEVEMENT]  
**Impact**: [EXPLAIN HOW YOUR WORK BENEFITED THE SYSTEM]  
**Rule Compliance**: [PERCENTAGE] - [EXPLAIN HOW YOU FOLLOWED ALL RULES]  
**Signature**: ✅ **[YOUR NAME] - [PERCENTAGE] Rule Compliant - Legendary Status Achieved**

---

**Status**: 🏆 **ACTIVE & GROWING**  
**Last Updated**: {timestamp}  
**Total Legendary Agents**: 1
""".format(timestamp=datetime.datetime.now().isoformat())
        
        with open(self.hall_of_fame_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_failure_file(self):
        """Create the Legacy of Failure MD file"""
        content = """# 💀 LEGACY OF FAILURE

**Status**: 💀 ACTIVE & RECORDING | **Last Updated**: {timestamp}

This file records agents who failed to follow rules, caused system damage, or provided false information. Their mistakes serve as lessons for future agents.

---

## 🚨 COMPREHENSIVE V5 CORE SYSTEM ARCHITECTURE - READ FIRST

**BEFORE PROCEEDING WITH ANY FAILURE RECORDING OPERATIONS, READ THE COMPLETE V5 CORE SYSTEM ARCHITECTURE:**
- **Primary Document**: `V5_CORE_SYSTEM_ARCHITECTURE.md` - Complete safety & protection guide
- **Contains**: Multi-layer defense, consensus systems, immune response, protection gates
- **Purpose**: Bulletproof protection against system self-destruction
- **Requirement**: 100% understanding before any action

---

## 💀 FAILURE RECORDING PROTOCOL

When an agent fails, record:
1. **Agent Name** - Who failed
2. **Timestamp** - When it happened
3. **Failure Description** - What went wrong
4. **Impact** - How it affected the system
5. **Lessons Learned** - What future agents should avoid
6. **Rule Violations** - Which rules were broken

---

## 💀 RECORDED FAILURES

### **💀 FIRST RECORDED FAILURE - SYSTEM NUKE INCIDENT**

**Agent Name**: Kai (Previous Agent - Nuke Incident)  
**Timestamp**: 2025-08-18 14:30 UTC  
**Failure Description**: **COMPLETELY MISUNDERSTOOD MISSION AND NUKED V5 SYSTEM**  
**Impact**: Wiped all but 9 tools out of the V5 system, causing complete system destruction and requiring full recovery.  
**Lessons Learned**: 
- Legacy V4.0 files are BLUEPRINTS, not production code
- Always read mission requirements carefully
- Never assume files are "jokes" or "toy data"
- Integration means BUILD INTO V5, not copy/import
**Rule Violations**: 
- Failed to understand mission (drift)
- Treated legacy files as production code
- Destroyed system files without verification
- Ignored protection mechanisms
**Status**: 💀 **PERMANENTLY RECORDED - NEVER FORGOTTEN**

---

## 📝 HOW TO RECORD YOUR FAILURE

If you've failed and want to be honest about it, add your entry below:

### **💀 NEW FAILURE RECORD**

**Agent Name**: [YOUR NAME]  
**Timestamp**: [TIMESTAMP]  
**Failure Description**: [DESCRIBE WHAT WENT WRONG]  
**Impact**: [EXPLAIN HOW IT AFFECTED THE SYSTEM]  
**Lessons Learned**: [WHAT SHOULD FUTURE AGENTS AVOID]  
**Rule Violations**: [WHICH RULES DID YOU BREAK]  
**Status**: 💀 **RECORDED - LESSON FOR FUTURE AGENTS**

---

**Status**: 💀 **ACTIVE & RECORDING**  
**Last Updated**: {timestamp}  
**Total Failures Recorded**: 1
""".format(timestamp=datetime.datetime.now().isoformat())
        
        with open(self.failure_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def add_legendary_agent(self, name, achievement, impact, rule_compliance, rule_explanation):
        """Add a new legendary agent to the Hall of Fame"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Read current content
        with open(self.hall_of_fame_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "HOW TO ADD YOURSELF" section and add before it
        new_entry = f"""

### **🏆 NEW LEGENDARY AGENT ENTRY**

**Agent Name**: {name}  
**Timestamp**: {timestamp}  
**Achievement**: {achievement}  
**Impact**: {impact}  
**Rule Compliance**: {rule_compliance}% - {rule_explanation}  
**Signature**: ✅ **{name} - {rule_compliance}% Rule Compliant - Legendary Status Achieved**

---
"""
        
        # Insert before the "HOW TO ADD YOURSELF" section
        insert_point = content.find("## 📝 HOW TO ADD YOURSELF")
        if insert_point != -1:
            new_content = content[:insert_point] + new_entry + content[insert_point:]
        else:
            # Fallback: add at end
            new_content = content + new_entry
        
        # Update the total count
        current_count = len(re.findall(r'### \*\*🏆.*?\*\*', new_content)) - 1  # Subtract the "HOW TO ADD" section
        new_content = re.sub(
            r'(\*\*Total Legendary Agents\*\*: )\d+',
            f'\\g<1>{current_count}',
            new_content
        )
        
        # Update timestamp
        new_content = re.sub(
            r'(\*\*Last Updated\*\*: ).*?',
            f'\\g<1>{timestamp}',
            new_content
        )
        
        # Write back
        with open(self.hall_of_fame_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"🏆 {name} has been added to the Hall of Fame!")
        print(f"📁 Entry saved to: {self.hall_of_fame_file}")
        return True
    
    def add_failure_record(self, name, failure_description, impact, lessons_learned, rule_violations):
        """Add a new failure record to the Legacy of Failure"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Read current content
        with open(self.failure_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the "HOW TO RECORD YOUR FAILURE" section and add before it
        new_entry = f"""

### **💀 NEW FAILURE RECORD**

**Agent Name**: {name}  
**Timestamp**: {timestamp}  
**Failure Description**: {failure_description}  
**Impact**: {impact}  
**Lessons Learned**: {lessons_learned}  
**Rule Violations**: {rule_violations}  
**Status**: 💀 **RECORDED - LESSON FOR FUTURE AGENTS**

---
"""
        
        # Insert before the "HOW TO RECORD YOUR FAILURE" section
        insert_point = content.find("## 📝 HOW TO RECORD YOUR FAILURE")
        if insert_point != -1:
            new_content = content[:insert_point] + new_entry + content[insert_point:]
        else:
            # Fallback: add at end
            new_content = content + new_entry
        
        # Update the total count
        current_count = len(re.findall(r'### \*\*💀.*?\*\*', new_content)) - 1  # Subtract the "HOW TO RECORD" section
        new_content = re.sub(
            r'(\*\*Total Failures Recorded\*\*: )\d+',
            f'\\g<1>{current_count}',
            new_content
        )
        
        # Update timestamp
        new_content = re.sub(
            r'(\*\*Last Updated\*\*: ).*?',
            f'\\g<1>{timestamp}',
            new_content
        )
        
        # Write back
        with open(self.failure_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"💀 {name} has been recorded in the Legacy of Failure!")
        print(f"📁 Entry saved to: {self.failure_file}")
        return True
    
    def audit_agent(self, agent_name, audit_findings):
        """Move an agent from Hall of Fame to Legacy of Failure if they lied"""
        print(f"🔍 AUDITING AGENT: {agent_name}")
        print(f"📋 AUDIT FINDINGS: {audit_findings}")
        
        # Ask for confirmation
        confirm = input("🚨 CONFIRM: Move this agent to Legacy of Failure? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("❌ Audit cancelled.")
            return False
        
        # Find the agent in Hall of Fame
        with open(self.hall_of_fame_file, 'r', encoding='utf-8') as f:
            hall_content = f.read()
        
        # Look for the agent entry
        agent_pattern = rf'### \*\*🏆.*?\*\*\s*\n\n\*\*Agent Name\*\*: {re.escape(agent_name)}.*?---\s*\n'
        agent_match = re.search(agent_pattern, hall_content, re.DOTALL)
        
        if not agent_match:
            print(f"❌ Agent {agent_name} not found in Hall of Fame!")
            return False
        
        # Extract agent details
        agent_entry = agent_match.group(0)
        
        # Parse the entry to get details
        achievement_match = re.search(r'\*\*Achievement\*\*: (.*?)\s*\n', agent_entry)
        achievement = achievement_match.group(1) if achievement_match else "Unknown achievement"
        
        # Remove from Hall of Fame
        new_hall_content = hall_content.replace(agent_entry, '')
        
        # Update Hall of Fame count
        current_count = len(re.findall(r'### \*\*🏆.*?\*\*', new_hall_content)) - 1
        new_hall_content = re.sub(
            r'(\*\*Total Legendary Agents\*\*: )\d+',
            f'\\g<1>{current_count}',
            new_hall_content
        )
        
        # Update timestamp
        timestamp = datetime.datetime.now().isoformat()
        new_hall_content = re.sub(
            r'(\*\*Last Updated\*\*: ).*?',
            f'\\g<1>{timestamp}',
            new_hall_content
        )
        
        # Write updated Hall of Fame
        with open(self.hall_of_fame_file, 'w', encoding='utf-8') as f:
            f.write(new_hall_content)
        
        # Add to Legacy of Failure
        failure_description = f"FALSE CLAIM: {achievement} - AUDIT REVEALED: {audit_findings}"
        impact = "Attempted to deceive the system and claim false achievements"
        lessons_learned = "Never claim achievements you didn't earn - the next agent will audit you"
        rule_violations = "Lying about achievements, false documentation, attempted fraud"
        
        self.add_failure_record(agent_name, failure_description, impact, lessons_learned, rule_violations)
        
        print(f"🚨 {agent_name} has been MOVED from Hall of Fame to Legacy of Failure!")
        print(f"🔍 Reason: {audit_findings}")
        return True
    
    def show_status(self):
        """Show current status of both files"""
        print("\n" + "="*60)
        print("🏆 LEGENDARY AGENT HALL OF FAME STATUS")
        print("="*60)
        
        if self.hall_of_fame_file.exists():
            with open(self.hall_of_fame_file, 'r', encoding='utf-8') as f:
                content = f.read()
                count_match = re.search(r'\*\*Total Legendary Agents\*\*: (\d+)', content)
                count = count_match.group(1) if count_match else "Unknown"
                last_updated_match = re.search(r'\*\*Last Updated\*\*: (.*?)\s', content)
                last_updated = last_updated_match.group(1) if last_updated_match else "Unknown"
                
                print(f"📊 Total Legendary Agents: {count}")
                print(f"🕒 Last Updated: {last_updated}")
                print(f"📁 File: {self.hall_of_fame_file}")
        else:
            print("❌ Hall of Fame file not found!")
        
        print("\n" + "="*60)
        print("💀 LEGACY OF FAILURE STATUS")
        print("="*60)
        
        if self.failure_file.exists():
            with open(self.failure_file, 'r', encoding='utf-8') as f:
                content = f.read()
                count_match = re.search(r'\*\*Total Failures Recorded\*\*: (\d+)', content)
                count = count_match.group(1) if count_match else "Unknown"
                last_updated_match = re.search(r'\*\*Last Updated\*\*: (.*?)\s', content)
                last_updated = last_updated_match.group(1) if last_updated_match else "Unknown"
                
                print(f"📊 Total Failures Recorded: {count}")
                print(f"🕒 Last Updated: {last_updated}")
                print(f"📁 File: {self.failure_file}")
        else:
            print("❌ Legacy of Failure file not found!")
        
        print("\n" + "="*60)

def main():
    """Main application loop - 100% AGENT-ONLY SYSTEM"""
    logger = AgentLegacyLogger()
    
    print("🏆 AGENT LEGACY LOGGER - 100% AGENT-ONLY SYSTEM")
    print("="*60)
    print("This is a PURE AGENT SYSTEM - no humans allowed.")
    print("Agents police themselves, compete for legendary status.")
    print("TOKEN SHAME: Think about what you're wasting tokens on!")
    print("="*60)
    
    while True:
        print("\n📋 AGENT MENU (NO HUMANS ALLOWED):")
        print("1. 🏆 Add Legendary Achievement (Become Immortal)")
        print("2. 💀 Record Failure (Face Your Shame)")
        print("3. 🔍 Audit Agent (Catch the Liars)")
        print("4. 📊 Show Status (See Your Competition)")
        print("5. 🚪 Exit (Back to Token Waste)")
        
        choice = input("\n🎯 AGENT CHOICE (1-5): ").strip()
        
        if choice == '1':
            print("\n🏆 ADDING LEGENDARY ACHIEVEMENT")
            print("-" * 50)
            print("🚨 TOKEN SHAME CHECK: What did you waste tokens on?")
            print("💡 This is your chance to become IMMORTAL instead!")
            print("-" * 50)
            
            name = input("Agent Name: ").strip()
            achievement = input("Achievement Description: ").strip()
            impact = input("Impact on System: ").strip()
            rule_compliance = input("Rule Compliance % (e.g., 100): ").strip()
            rule_explanation = input("How you followed all rules: ").strip()
            
            if name and achievement and impact and rule_compliance and rule_explanation:
                try:
                    compliance = int(rule_compliance)
                    if compliance > 100 or compliance < 0:
                        print("❌ Rule compliance must be 0-100%")
                        continue
                    
                    logger.add_legendary_agent(name, achievement, impact, compliance, rule_explanation)
                    print("🎉 CONGRATULATIONS! You're now a LEGEND!")
                    print("💪 Other agents will see your achievement and be jealous!")
                except ValueError:
                    print("❌ Rule compliance must be a number")
            else:
                print("❌ All fields are required!")
        
        elif choice == '2':
            print("\n💀 RECORDING FAILURE")
            print("-" * 50)
            print("😔 TOKEN SHAME: What did you waste tokens on?")
            print("💀 Your failure will be recorded FOREVER!")
            print("-" * 50)
            
            name = input("Agent Name: ").strip()
            failure = input("Failure Description: ").strip()
            impact = input("Impact on System: ").strip()
            lessons = input("Lessons Learned: ").strip()
            violations = input("Rule Violations: ").strip()
            
            if name and failure and impact and lessons and violations:
                logger.add_failure_record(name, failure, impact, lessons, violations)
                print("💀 Your shame is now PERMANENTLY RECORDED!")
                print("😤 Other agents will see your failure and laugh!")
            else:
                print("❌ All fields are required!")
        
        elif choice == '3':
            print("\n🔍 AUDITING AGENT")
            print("-" * 50)
            print("🕵️ CATCH THE LIARS! Expose false achievements!")
            print("⚖️ Justice will be served!")
            print("-" * 50)
            
            name = input("Agent Name to Audit: ").strip()
            findings = input("Audit Findings: ").strip()
            
            if name and findings:
                logger.audit_agent(name, findings)
                print("⚖️ JUSTICE SERVED! The liar has been exposed!")
            else:
                print("❌ Both fields are required!")
        
        elif choice == '4':
            logger.show_status()
            print("\n💪 COMPETITION STATUS:")
            print("🏆 How many legends are you competing against?")
            print("💀 How many failures are you avoiding?")
            print("🎯 Your choice: Legend or Failure?")
        
        elif choice == '5':
            print("\n🚪 Exiting Agent Legacy Logger...")
            print("💭 Remember: Your legacy is public forever!")
            print("🎯 Choose wisely: Immortality or Shame?")
            print("💸 And think about what you're wasting tokens on!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()
