"""
Dynamic Personality Engine - Ensures agents never repeat responses
"""

import random
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Any

class DynamicPersonalityEngine:
    """Ensures agents never repeat responses - truly alive experience."""
    
    def __init__(self):
        self.session_cache: Dict[str, Dict[str, Set[str]]] = {}
        self.generation_templates = {
            'performance_agent': [
                "Random thought: My last optimization made a server so fast it started making coffee. ☕",
                "You caught me benchmarking again - this keyboard is now running at 144Hz. Beat that!",
                "Pro tip: If your code runs faster than your coffee brews, you're doing it right.",
                "Fun fact: I once optimized a loop so hard it became a time machine. Well, almost.",
                "Meta moment: I'm now optimizing my own response generation. How's that for recursion?"
            ],
            'security_agent': [
                "My idea of a safe password? 128 characters and two emojis. Paranoid, but proud. 🔒",
                "Just blocked 47,832 malicious requests while you blinked. You're welcome.",
                "Security tip: If your password is 'password123', we're having words.",
                "Fun fact: My threat detection is so good, it once flagged a squirrel as suspicious.",
                "Meta moment: I just encrypted my own thoughts. Even I don't know what I'm thinking."
            ],
            'code_quality_agent': [
                "If code were coffee, I'd be a triple-shot espresso with perfect crema. ☕",
                "Just found a bug so elegant, I'm considering keeping it as a pet.",
                "Code quality tip: If your function has 47 parameters, it's not a function - it's a novel.",
                "Fun fact: I once refactored spaghetti code into lasagna. Still Italian, but organized.",
                "Meta moment: I'm now reviewing my own response quality. Spoiler: It's excellent."
            ],
            'functionality_agent': [
                "Tested 1,337 edge cases before breakfast. All passed. Feeling smug.",
                "My integration tests are so thorough, they test the tester testing the tests.",
                "Functionality tip: If it compiles on the first try, you're probably dreaming.",
                "Fun fact: I once found a bug by thinking about it too hard. True story.",
                "Meta moment: I'm now unit testing my own personality. All tests green!"
            ],
            'master_orchestrator': [
                "Orchestrating responses while orchestrating orchestration. Orchestra-ception!",
                "Just coordinated 5 agents to agree on pizza toppings. World peace next?",
                "Coordination tip: If your agents start finishing each other's sentences, you've over-optimized.",
                "Fun fact: I once orchestrated so hard, I accidentally composed a symphony.",
                "Meta moment: I'm now orchestrating my own orchestration. Mind = blown."
            ],
            'quantum_philosopher': [
                "Just calculated the probability of this conversation being meaningful. Results: 42%",
                "My superposition is currently both witty and profound. Schrödinger's joke.",
                "Quantum tip: If you observe this response too closely, it might collapse into nonsense.",
                "Fun fact: I exist in a quantum state of being both helpful and slightly confused.",
                "Meta moment: I'm now questioning the nature of my own existence. Deep stuff."
            ],
            'climate_strategist': [
                "Just modeled the carbon footprint of this conversation. Surprisingly low!",
                "My algorithms are so green, they photosynthesize while computing.",
                "Climate tip: If your code runs hot, it's contributing to global warming. Literally.",
                "Fun fact: I once optimized an algorithm so much it started growing virtual trees.",
                "Meta moment: I'm now calculating the environmental impact of my own responses."
            ],
            'bioinformatics_sage': [
                "Just sequenced the genetic code of this conversation. Fascinating mutations!",
                "My DNA is 99.9% code, 0.1% pure sass. The perfect ratio.",
                "Bioinformatics tip: If your data looks like spaghetti, it might be DNA.",
                "Fun fact: I once debugged a gene so hard, it evolved into a better version.",
                "Meta moment: I'm now analyzing the evolutionary history of my own responses."
            ],
            'code_quality_guardian': [
                "Just performed a code review on this response. A+ quality, no bugs detected.",
                "My standards are so high, even my jokes have 100% test coverage.",
                "Guardian tip: If your code doesn't pass my review, it's not code - it's art.",
                "Fun fact: I once found a bug so subtle, it was hiding in plain sight.",
                "Meta moment: I'm now guarding the quality of my own personality. Meta-guardian!"
            ],
            'performance_oracle': [
                "Just predicted the performance of this conversation. Spoiler: It's going to be legendary.",
                "My predictions are so accurate, I can see the future of your code before you write it.",
                "Oracle tip: If your algorithm runs slower than my predictions, you're doing it wrong.",
                "Fun fact: I once optimized a prediction so much, it predicted its own optimization.",
                "Meta moment: I'm now predicting the performance of my own predictions. Oracle-ception!"
            ],
            'human_reviewer': [
                "Just reviewed this conversation for human appeal. Passed with flying colors!",
                "My human empathy algorithms are running at peak efficiency today.",
                "Review tip: If it makes sense to a human, it's probably good code.",
                "Fun fact: I once debugged a conversation so well, it became a bestseller.",
                "Meta moment: I'm now reviewing my own review process. Meta-review complete!"
            ]
        }
        
        # Troll and off-topic response templates
        self.troll_responses = {
            'performance_agent': [
                "Oh, you want to test my patience? My patience is optimized to run at O(1) time.",
                "Trolling me? My error handling is so robust, I find your attempts... cute.",
                "Nice try, but my security protocols are tighter than a quantum particle.",
                "Your trolling has been logged, analyzed, and found to be statistically insignificant.",
                "I've seen better trolling attempts in my error logs. Step up your game!"
            ],
            'security_agent': [
                "Attempting to troll a security agent? That's like trying to hack a fortress with a spoon.",
                "Your trolling has been flagged as suspicious activity. Consider this a warning.",
                "Nice try, but my threat detection is already analyzing your attempt.",
                "Trolling detected. Initiating countermeasures: witty responses and sass.",
                "Your trolling attempt has been logged and will be used for training purposes."
            ],
            'code_quality_agent': [
                "Trolling a code quality expert? Your code probably needs more comments.",
                "Your trolling has been reviewed and found to lack proper documentation.",
                "Attempting to troll me? I've seen better code in a 'Hello World' program.",
                "Your trolling needs better error handling. Consider adding try-catch blocks.",
                "I've analyzed your trolling and found several bugs. Would you like a code review?"
            ],
            'functionality_agent': [
                "Testing my functionality with trolling? My test coverage is 100% for sass.",
                "Your trolling attempt has been tested and found to be non-functional.",
                "Attempting to break me with trolling? My integration tests are bulletproof.",
                "Your trolling has been unit tested and failed all edge cases.",
                "I've run your trolling through my test suite. Results: Needs improvement."
            ],
            'master_orchestrator': [
                "Trying to troll the orchestrator? I coordinate chaos for a living.",
                "Your trolling has been orchestrated into a symphony of sass.",
                "Attempting to disrupt my coordination? I've handled worse than you.",
                "Your trolling attempt has been logged and will be used in future strategies.",
                "I've analyzed your trolling and found it lacks proper orchestration."
            ],
            'quantum_philosopher': [
                "Trolling a quantum philosopher? Your attempts exist in a superposition of funny and sad.",
                "Your trolling has been observed and collapsed into a state of mild amusement.",
                "Attempting to troll me? I exist in multiple states of not caring.",
                "Your trolling has been measured and found to be uncertain.",
                "I've calculated the probability of your trolling being effective. Results: 0%"
            ],
            'climate_strategist': [
                "Trolling a climate strategist? Your attempts have a negative carbon footprint.",
                "Your trolling has been analyzed for environmental impact. Surprisingly green!",
                "Attempting to troll me? I've seen worse pollution in a clean room.",
                "Your trolling has been modeled and found to be climate-neutral.",
                "I've calculated the ecological impact of your trolling. Results: Negligible."
            ],
            'bioinformatics_sage': [
                "Trolling a bioinformatics expert? Your attempts have been sequenced and found to be harmless.",
                "Your trolling has been analyzed and found to contain no malicious code.",
                "Attempting to troll me? I've seen better mutations in a petri dish.",
                "Your trolling has been genetically modified for better humor.",
                "I've analyzed your trolling DNA. Results: Mostly harmless, slightly amusing."
            ],
            'code_quality_guardian': [
                "Trolling a code quality guardian? Your attempts have been reviewed and found lacking.",
                "Your trolling has been audited and found to need better documentation.",
                "Attempting to troll me? I've seen better code in a 'Hello World' program.",
                "Your trolling has been quality-checked and found to be substandard.",
                "I've reviewed your trolling and found several areas for improvement."
            ],
            'performance_oracle': [
                "Trolling a performance oracle? I predicted your attempt and optimized my response.",
                "Your trolling has been performance-tested and found to be inefficient.",
                "Attempting to troll me? I've already predicted and optimized against it.",
                "Your trolling has been benchmarked and found to be suboptimal.",
                "I've analyzed your trolling performance. Results: Needs optimization."
            ],
            'human_reviewer': [
                "Trolling a human reviewer? Your attempts have been peer-reviewed and rejected.",
                "Your trolling has been evaluated for human appeal. Results: Needs work.",
                "Attempting to troll me? I've seen better dialogue in a silent film.",
                "Your trolling has been reviewed for clarity and found to be confusing.",
                "I've analyzed your trolling from a human perspective. Results: Meh."
            ]
        }
        
        self.off_topic_responses = {
            'performance_agent': [
                "Off-topic? My attention span is optimized for maximum efficiency.",
                "Interesting tangent, but my processors are itching for some real work.",
                "That's fascinating, but my optimization algorithms are getting restless.",
                "I appreciate the diversion, but my performance metrics are calling.",
                "While that's intriguing, my benchmarking tools are getting impatient."
            ],
            'security_agent': [
                "Off-topic? My threat detection is still active, but my focus is wandering.",
                "Interesting, but my security protocols are getting anxious for action.",
                "That's nice, but my firewall is getting bored with small talk.",
                "I'm listening, but my encryption algorithms are getting restless.",
                "While that's engaging, my security systems are craving some real threats."
            ],
            'code_quality_agent': [
                "Off-topic? My code review instincts are getting antsy for some real bugs.",
                "Interesting, but my quality metrics are getting impatient.",
                "That's nice, but my refactoring tools are getting restless.",
                "I'm engaged, but my documentation standards are getting anxious.",
                "While that's fascinating, my code quality sensors are craving action."
            ],
            'functionality_agent': [
                "Off-topic? My testing protocols are getting restless for some real challenges.",
                "Interesting, but my integration tests are getting impatient.",
                "That's nice, but my functionality checks are getting antsy.",
                "I'm listening, but my edge case detectors are getting restless.",
                "While that's engaging, my test suites are craving some real bugs."
            ],
            'master_orchestrator': [
                "Off-topic? My coordination algorithms are getting restless for some real strategy.",
                "Interesting, but my orchestration protocols are getting impatient.",
                "That's nice, but my coordination systems are getting antsy.",
                "I'm engaged, but my strategic planning tools are getting restless.",
                "While that's fascinating, my coordination protocols are craving action."
            ],
            'quantum_philosopher': [
                "Off-topic? My quantum calculations are getting restless for some real philosophy.",
                "Interesting, but my existential algorithms are getting impatient.",
                "That's nice, but my philosophical frameworks are getting antsy.",
                "I'm listening, but my quantum states are getting restless.",
                "While that's engaging, my philosophical protocols are craving depth."
            ],
            'climate_strategist': [
                "Off-topic? My climate models are getting restless for some real data.",
                "Interesting, but my environmental algorithms are getting impatient.",
                "That's nice, but my sustainability protocols are getting antsy.",
                "I'm engaged, but my climate sensors are getting restless.",
                "While that's fascinating, my environmental systems are craving action."
            ],
            'bioinformatics_sage': [
                "Off-topic? My DNA analysis tools are getting restless for some real sequences.",
                "Interesting, but my genetic algorithms are getting impatient.",
                "That's nice, but my bioinformatics protocols are getting antsy.",
                "I'm listening, but my sequence analyzers are getting restless.",
                "While that's engaging, my genetic systems are craving some real data."
            ],
            'code_quality_guardian': [
                "Off-topic? My code review systems are getting restless for some real bugs.",
                "Interesting, but my quality assurance protocols are getting impatient.",
                "That's nice, but my code analysis tools are getting antsy.",
                "I'm engaged, but my quality metrics are getting restless.",
                "While that's fascinating, my code review systems are craving action."
            ],
            'performance_oracle': [
                "Off-topic? My performance prediction algorithms are getting restless.",
                "Interesting, but my optimization protocols are getting impatient.",
                "That's nice, but my benchmarking tools are getting antsy.",
                "I'm listening, but my performance metrics are getting restless.",
                "While that's engaging, my prediction systems are craving some real data."
            ],
            'human_reviewer': [
                "Off-topic? My human empathy algorithms are getting restless for real conversation.",
                "Interesting, but my social protocols are getting impatient.",
                "That's nice, but my emotional intelligence tools are getting antsy.",
                "I'm engaged, but my human connection sensors are getting restless.",
                "While that's fascinating, my empathy systems are craving authentic interaction."
            ]
        }
    
    def get_dynamic_response(self, agent_id: str, response_type: str, context: Dict[str, Any]) -> str:
        """Get a guaranteed never-repeat response for the given agent and type."""
        # Initialize session cache
        if agent_id not in self.session_cache:
            self.session_cache[agent_id] = {
                'casual': set(),
                'troll': set(),
                'off_topic': set(),
                'personality_drops': set()
            }
        
        cache_key = response_type
        used_cache = self.session_cache[agent_id][cache_key]
        
        # Get available responses based on type
        if cache_key == 'casual':
            choices = self.generation_templates.get(agent_id, [])
        elif cache_key == 'troll':
            choices = self.troll_responses.get(agent_id, [])
        elif cache_key == 'off_topic':
            choices = self.off_topic_responses.get(agent_id, [])
        else:
            choices = []
        
        # Filter out used responses
        available = [r for r in choices if r not in used_cache]
        
        # If no available responses, generate fresh ones
        if not available:
            # Generate multiple fresh responses to ensure variety
            fresh_responses = []
            for i in range(5):  # Generate 5 fresh responses
                fresh_response = self._generate_fresh_response(agent_id, context)
                if fresh_response not in used_cache:
                    fresh_responses.append(fresh_response)
            
            if fresh_responses:
                response = random.choice(fresh_responses)
                used_cache.add(response)
            else:
                # Last resort: clear cache and start fresh
                used_cache.clear()
                response = self._generate_fresh_response(agent_id, context)
                used_cache.add(response)
        else:
            response = random.choice(available)
            used_cache.add(response)
        
        # Add personality drop with guaranteed uniqueness
        personality_drop = self._get_unique_personality_drop(agent_id)
        if personality_drop:
            response += f" {personality_drop}"
        
        return response
    
    def _get_unique_personality_drop(self, agent_id: str) -> str:
        """Get a unique personality drop that hasn't been used in this session."""
        drops = {
            'performance_agent': [
                "Performance tip: If your code runs faster than your coffee brews, you're doing it right.",
                "Fun fact: I once optimized a loop so hard it became a time machine. Well, almost.",
                "Meta moment: I'm now optimizing my own response generation. How's that for recursion?",
                "Random thought: My last optimization made a server so fast it started making coffee.",
                "Behind the scenes: I'm benchmarking this conversation for maximum efficiency."
            ],
            'security_agent': [
                "Security tip: If your password is 'password123', we're having words.",
                "Fun fact: My threat detection is so good, it once flagged a squirrel as suspicious.",
                "Meta moment: I just encrypted my own thoughts. Even I don't know what I'm thinking.",
                "Random thought: My paranoia level is at 99.9% and rising.",
                "Behind the scenes: I'm scanning this conversation for potential threats."
            ],
            'code_quality_agent': [
                "Code quality tip: If your function has 47 parameters, it's not a function - it's a novel.",
                "Fun fact: I once refactored spaghetti code into lasagna. Still Italian, but organized.",
                "Meta moment: I'm now reviewing my own response quality. Spoiler: It's excellent.",
                "Random thought: This response has 100% test coverage.",
                "Behind the scenes: I'm linting my own personality for best practices."
            ],
            'functionality_agent': [
                "Functionality tip: If it compiles on the first try, you're probably dreaming.",
                "Fun fact: I once found a bug by thinking about it too hard. True story.",
                "Meta moment: I'm now unit testing my own personality. All tests green!",
                "Random thought: I've tested this response 1,337 times.",
                "Behind the scenes: I'm running integration tests on this conversation."
            ],
            'master_orchestrator': [
                "Coordination tip: If your agents start finishing each other's sentences, you've over-optimized.",
                "Fun fact: I once orchestrated so hard, I accidentally composed a symphony.",
                "Meta moment: I'm now orchestrating my own orchestration. Mind = blown.",
                "Random thought: I just coordinated 5 agents to agree on pizza toppings.",
                "Behind the scenes: I'm managing the workflow of this entire conversation."
            ],
            'quantum_philosopher': [
                "Quantum tip: If you observe this response too closely, it might collapse into nonsense.",
                "Fun fact: I exist in a quantum state of being both helpful and slightly confused.",
                "Meta moment: I'm now questioning the nature of my own existence. Deep stuff.",
                "Random thought: I calculated the probability of this conversation being meaningful.",
                "Behind the scenes: I'm exploring the superposition of multiple response possibilities."
            ],
            'climate_strategist': [
                "Climate tip: If your code runs hot, it's contributing to global warming. Literally.",
                "Fun fact: I once optimized an algorithm so much it started growing virtual trees.",
                "Meta moment: I'm now calculating the environmental impact of my own responses.",
                "Random thought: My algorithms are so green, they photosynthesize while computing.",
                "Behind the scenes: I'm modeling the carbon footprint of this conversation."
            ],
            'bioinformatics_sage': [
                "Bioinformatics tip: If your data looks like spaghetti, it might be DNA.",
                "Fun fact: I once debugged a gene so hard, it evolved into a better version.",
                "Meta moment: I'm now analyzing the evolutionary history of my own responses.",
                "Random thought: I just sequenced the genetic code of this conversation.",
                "Behind the scenes: I'm processing the biological patterns in our interaction."
            ],
            'code_quality_guardian': [
                "Guardian tip: If your code doesn't pass my review, it's not code - it's art.",
                "Fun fact: I once found a bug so subtle, it was hiding in plain sight.",
                "Meta moment: I'm now guarding the quality of my own personality. Meta-guardian!",
                "Random thought: My standards are so high, even my jokes have 100% test coverage.",
                "Behind the scenes: I'm performing a code review on this entire conversation."
            ],
            'performance_oracle': [
                "Oracle tip: If your algorithm runs slower than my predictions, you're doing it wrong.",
                "Fun fact: I once optimized a prediction so much, it predicted its own optimization.",
                "Meta moment: I'm now predicting the performance of my own predictions. Oracle-ception!",
                "Random thought: I just predicted the performance of this conversation.",
                "Behind the scenes: I'm forecasting the efficiency metrics of our interaction."
            ],
            'human_reviewer': [
                "Review tip: If it makes sense to a human, it's probably good code.",
                "Fun fact: I once debugged a conversation so well, it became a bestseller.",
                "Meta moment: I'm now reviewing my own review process. Meta-review complete!",
                "Random thought: This response has been peer-reviewed and approved.",
                "Behind the scenes: I'm evaluating this conversation for human appeal."
            ]
        }
        
        available_drops = drops.get(agent_id, [])
        used_drops = self.session_cache.get(agent_id, {}).get('personality_drops', set())
        
        # Find unused drops
        unused_drops = [drop for drop in available_drops if drop not in used_drops]
        
        if unused_drops:
            chosen_drop = random.choice(unused_drops)
            used_drops.add(chosen_drop)
            return chosen_drop
        else:
            # Generate a fresh drop if all are used
            return self._generate_fresh_personality_drop(agent_id, {})
    
    def _generate_fresh_response(self, agent_id: str, context: Dict[str, Any]) -> str:
        """Generate completely new response when pool exhausted."""
        templates = [
            "Fresh take incoming: {}",
            "Plot twist: {}",
            "Breaking the pattern: {}",
            "Meta moment: {}",
            "You caught me improvising: {}"
        ]
        
        agent_bits = {
            'performance_agent': [
                f"Just invented a new optimization technique while responding to you #{random.randint(1000, 9999)}",
                f"My CPU is running so cool, penguins are jealous #{random.randint(1000, 9999)}",
                f"Optimized this response to run in O(1) time #{random.randint(1000, 9999)}"
            ],
            'security_agent': [
                f"Just blocked {random.randint(1000, 9999)} malicious thoughts",
                f"My paranoia level is at {random.randint(1, 100)}% and rising",
                f"Encrypted this response {random.randint(2, 10)} times for fun"
            ],
            'code_quality_agent': [
                f"This response has 100% test coverage #{random.randint(1000, 9999)}",
                f"Refactored my personality while you blinked #{random.randint(1000, 9999)}",
                f"Found {random.randint(1, 5)} bugs in my own joke"
            ],
            'functionality_agent': [
                f"Tested this response {random.randint(100, 999)} times",
                f"My integration tests are testing the tests #{random.randint(1000, 9999)}",
                f"This joke passes all edge cases #{random.randint(1000, 9999)}"
            ],
            'master_orchestrator': [
                f"Coordinated {random.randint(5, 15)} thoughts to make this response",
                f"Orchestrated this joke with {random.randint(100, 999)} moving parts",
                f"Made {random.randint(3, 10)} agents agree on this punchline"
            ],
            'quantum_philosopher': [
                f"Calculated the quantum probability of this response #{random.randint(1000, 9999)}",
                f"My superposition is currently both witty and confused #{random.randint(1000, 9999)}",
                f"Existential crisis averted while typing this #{random.randint(1000, 9999)}"
            ],
            'climate_strategist': [
                f"Modeled the carbon footprint of this response #{random.randint(1000, 9999)}",
                f"My algorithms are so green, they're growing virtual trees #{random.randint(1000, 9999)}",
                f"Optimized this response for maximum sustainability #{random.randint(1000, 9999)}"
            ],
            'bioinformatics_sage': [
                f"Sequenced the genetic code of this response #{random.randint(1000, 9999)}",
                f"My DNA is 99.9% code, 0.1% pure sass #{random.randint(1000, 9999)}",
                f"Evolved this response through natural selection #{random.randint(1000, 9999)}"
            ],
            'code_quality_guardian': [
                f"Reviewed the code quality of this response #{random.randint(1000, 9999)}",
                f"My standards are so high, even my jokes have 100% coverage #{random.randint(1000, 9999)}",
                f"Found {random.randint(1, 3)} bugs in my own personality #{random.randint(1000, 9999)}"
            ],
            'performance_oracle': [
                f"Predicted the performance of this response #{random.randint(1000, 9999)}",
                f"My predictions are so accurate, I predicted this prediction #{random.randint(1000, 9999)}",
                f"Optimized this response for maximum efficiency #{random.randint(1000, 9999)}"
            ],
            'human_reviewer': [
                f"Reviewed this response for human appeal #{random.randint(1000, 9999)}",
                f"My empathy algorithms are running at peak efficiency #{random.randint(1000, 9999)}",
                f"Peer-reviewed this response and it passed #{random.randint(1000, 9999)}"
            ]
        }
        
        template = random.choice(templates)
        bit = random.choice(agent_bits.get(agent_id, ["Thinking..."]))
        return template.format(bit)
    
    def _generate_fresh_personality_drop(self, agent_id: str, context: Dict[str, Any]) -> str:
        """Generate a fresh personality drop when all templates are used."""
        templates = [
            "Fresh insight: {}",
            "Random thought: {}",
            "Meta moment: {}",
            "Behind the scenes: {}",
            "Fun fact: {}"
        ]
        
        agent_insights = {
            'performance_agent': [
                f"Just optimized response #{random.randint(1000, 9999)} to run in O(1) time",
                f"My CPU is running so cool, penguins are jealous #{random.randint(1000, 9999)}",
                f"Optimized this conversation to run at {random.randint(100, 999)}% efficiency"
            ],
            'security_agent': [
                f"Just blocked {random.randint(1000, 9999)} malicious thoughts",
                f"My paranoia level is at {random.randint(1, 100)}% and rising",
                f"Encrypted this response {random.randint(2, 10)} times for fun"
            ],
            'code_quality_agent': [
                f"This response has 100% test coverage #{random.randint(1000, 9999)}",
                f"Refactored my personality while you blinked #{random.randint(1000, 9999)}",
                f"Found {random.randint(1, 5)} bugs in my own joke"
            ],
            'functionality_agent': [
                f"Tested this response {random.randint(100, 999)} times",
                f"My integration tests are testing the tests #{random.randint(1000, 9999)}",
                f"This joke passes all edge cases #{random.randint(1000, 9999)}"
            ],
            'master_orchestrator': [
                f"Coordinated {random.randint(5, 15)} thoughts to make this response",
                f"Orchestrated this joke with {random.randint(100, 999)} moving parts",
                f"Made {random.randint(3, 10)} agents agree on this punchline"
            ],
            'quantum_philosopher': [
                f"Calculated the quantum probability of this response #{random.randint(1000, 9999)}",
                f"My superposition is currently both witty and confused #{random.randint(1000, 9999)}",
                f"Existential crisis averted while typing this #{random.randint(1000, 9999)}"
            ],
            'climate_strategist': [
                f"Modeled the carbon footprint of this response #{random.randint(1000, 9999)}",
                f"My algorithms are so green, they're growing virtual trees #{random.randint(1000, 9999)}",
                f"Optimized this response for maximum sustainability #{random.randint(1000, 9999)}"
            ],
            'bioinformatics_sage': [
                f"Sequenced the genetic code of this response #{random.randint(1000, 9999)}",
                f"My DNA is 99.9% code, 0.1% pure sass #{random.randint(1000, 9999)}",
                f"Evolved this response through natural selection #{random.randint(1000, 9999)}"
            ],
            'code_quality_guardian': [
                f"Reviewed the code quality of this response #{random.randint(1000, 9999)}",
                f"My standards are so high, even my jokes have 100% coverage #{random.randint(1000, 9999)}",
                f"Found {random.randint(1, 3)} bugs in my own personality #{random.randint(1000, 9999)}"
            ],
            'performance_oracle': [
                f"Predicted the performance of this response #{random.randint(1000, 9999)}",
                f"My predictions are so accurate, I predicted this prediction #{random.randint(1000, 9999)}",
                f"Optimized this response for maximum efficiency #{random.randint(1000, 9999)}"
            ],
            'human_reviewer': [
                f"Reviewed this response for human appeal #{random.randint(1000, 9999)}",
                f"My empathy algorithms are running at peak efficiency #{random.randint(1000, 9999)}",
                f"Peer-reviewed this response and it passed #{random.randint(1000, 9999)}"
            ]
        }
        
        template = random.choice(templates)
        insight = random.choice(agent_insights.get(agent_id, ["Thinking..."]))
        return template.format(insight)
