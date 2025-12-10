# Content Analysis: SPAUN 3.0 - A Next Generation Large-Scale Brain Model

## Overview

This is a comprehensive technical presentation by Chris Eliasmith detailing SPAUN 3.0, the third generation of the world's largest functional brain model. Unlike the previous talk (Vision Weekend Europe 2024), this presentation is a deep dive into the technical architecture, theoretical foundations, neuroscience validation, and AI integration methods. Eliasmith emphasizes the bidirectional relationship between brain modeling and AI, showing how brain-inspired architectures can solve current AI limitations.

**Speaker**: Chris Eliasmith
**Topic**: SPAUN 3.0 Work in Progress
**Video URL**: https://www.youtube.com/watch?v=J2TMdwNZjSA

---

## Key Findings

### 1. Core Limitations of Current AI (Motivation for Brain Models)

**Sample Inefficient Learning**
- Current large AI models require massive amounts of data
- Lack appropriate inductive biases for efficient learning
- Biological intelligence learns with far fewer examples

**Imprecise Reasoning**
- LLMs struggle with simple algorithmic tasks (e.g., 3-digit multiplication)
- Humans follow reliable cognitive algorithms to solve problems accurately
- LLMs lack step-by-step procedural execution capabilities

> "And you also find in LLMs in particular a lot of imprecise reasoning, right. So if you try to get it to do uh simple math, what we would consider simple math, you know, I give you two three-digit numbers to multiply together, you can sit down and you can do that and you can do it accurately and typically you're following some kind of algorithm in your cognitive uh sort of reasoning and that gets you to the right answer. These models don't seem to be able to do that kind of thing"

**Brain Models as Solution**
- Uncover principles missed in functional AI approaches
- Induce right inductive biases for sample efficiency
- Incorporate precise reasoning through structured representations

### 2. Neural Engineering Framework (NEF)

**Foundational Theory (2003)**
- Published in "Neural Engineering" by Eliasmith & Anderson
- Functions as a "neural compiler" for brain models
- Remains the core methodology for SPAUN through all generations

**Three Core Principles**

1. **Representation**: High-dimensional vector representations
2. **Computation**: Nonlinear functions over representations
3. **Dynamics**: Embedding high-level dynamics into neural constraints

**Key Capability**
- Specify function as differential equation (e.g., dX/dt = 0 for working memory)
- Automatically compiles into spiking neural network
- Preserves biological constraints (neurotransmitters, connection types, time constants)

> "So you write down a differential equation of some kind. So if you're doing working memory could write down the differential equation dxdt equals z. Right? So whatever I stick in the memory just stays there. Doesn't change over time. That's a memory."

**Applications**
- Neural controllers
- Memory systems
- Decision-making circuits
- General-purpose brain computation

### 3. SPAUN Architecture Evolution

**SPAUN 1.0 (2012)**
- Published in Science and book chapter
- 2.5 million neurons, 7.5 billion connections
- 8 different cognitive tasks
- Anatomical and physiological mappings

**SPAUN 2.0 (2018)**
- 6 million neurons, 20 billion connections
- 12 different cognitive tasks
- 4 types of neurotransmitters
- Largest recurrent neural network (feedforward models don't count)
- Functional model that controls body and executes tasks

**Development Cycle**
- Every 6 years, lab integrates individual student/postdoc models
- Students work on specific areas (navigation, motor control, vision, learning)
- Integration creates capabilities beyond individual components
- "Whole is greater than sum of its parts"

> "essentially what's happened since the publication of spawn one is that every six years or so, we put together all of the new models and methods and techniques that different individual students or posttos have been working on in the lab"

**Key Architectural Components**

*Anatomical View*:
- Posterior parietal cortex
- Motor areas (M1, SMA)
- Basal ganglia (subcortical, inhibitory)
- Visual system (ventral stream)
- Anterior inferotemporal cortex
- Thalamus (subcortical)

*Functional View*:
- Visual encoding
- Working memory storage
- Motor decoding
- Reward evaluation
- Transform calculations (for reasoning tasks)
- Action selection (basal ganglia as information flow controller)

> "this is just a bunch of different information processing combined in different ways to perform the tasks that it performs right so things like processing the visual input and encoding it. Being able to store information over time"

### 4. The Continuous Representation Problem

**Critical Limitation of SPAUN 2.0**
- Most high-level representations were **discrete**
- Good for: Language-like structures, digit tasks, list memory
- Bad for: Continuous maps, spatial navigation, temporal distances

**Discrete Working Memory**
- Virtual slots holding discrete items (digits)
- Can answer "what's in slot 2?" but not "how far apart in time?"
- Loses temporal and spatial continuity information

**The Temporal Continuity Problem**

Traditional working memory tests:
- Give list of items, ask for recall in order (serial recall)
- Or recall in any order (free recall)
- Only tests **order**, not **temporal duration**

> "But if you think about your own working memory, it's temporal, right. So you don't you do care about the order things happen in, but you also know how far apart they were in time, right?"

Real working memory example:
- Lunch sequence: lined up → picked up food → sat down → ate → conversation
- You remember **order** AND **how long each took**
- Most models can't capture duration information

**Continuous Space Requirements**
- Maps need features at **any** position (not discrete slots)
- Navigation requires continuous spatial representations
- Example: Jug can be "in corner" or "1 meter from door" or "floating" - arbitrary positions

> "in a map you can think of a map as having continuous slots right like every every position in space there could be a thing sitting there right at every metric position"

### 5. Vector Symbolic Architectures (VSA) - The Breakthrough

**What are VSAs?**
- Mathematical framework for structured representations
- Operations: binding, unbinding, similarity, addition
- Used in SPAUN 2.0 for discrete representations (language-like structures)

**Key Insight**
- **Same operators can define continuous slots in maps!**
- Extends from discrete to continuous domains
- Unified framework for both discrete and continuous representations

**Capabilities with VSA**
- Define slots and bind fillers
- Multiple slots combined together
- Similarity operations between representations
- Unbinding to extract information

**Applications in SPAUN 3.0**
- Navigation
- Path integration
- **Replicates hippocampal cells**: place cells, grid cells, time cells
- Continuous space and time representations

> "interestingly those same operators can actually be used to define continuous slots in maps as well. Um and so this is something that we've been working on recently and we're introducing into spawn 3"

### 6. State Space Models - Connection to Modern AI

**Discovery Timeline**
- Eliasmith's lab published first state space model (2018-2019)
- Originated from modeling **time cells** in hippocampus
- Now recognized in AI as "next generation transformers"

**Key Properties**
- Much more efficient than transformers
- Introduces dynamics into neural networks
- Good at representing continuous time
- Enables language model integration into SPAUN

> "uh this has actually turned into uh what people in the AI literature know as statebased models, right? So these are kind of often touted as the next generation of transformer. They're much more efficient and so on. Uh and so we published the first uh state space model uh back in 2018 2019"

**Biology → AI Connection**
- Brain modeling (time cells) led to state space models
- State space models improve AI efficiency
- Now being reintegrated into brain models (SPAUN 3.0)
- Circular cross-fertilization

### 7. SPAUN 3.0 - Major Advances

**Infrastructure**
- **Isaac Sim**: Physics engine and 3D visualizer
- **Nengo**: Open-source spiking neural network simulator (from Eliasmith's lab)
- Goal: All SPAUN 2.0 capabilities + new embodied skills

**New Capabilities**

1. **3D Embodiment**
   - Full body in 3D world (not just eye and arm)
   - Walking and navigation
   - Foraging behaviors

2. **SLAM (Simultaneous Localization and Mapping)**
   - Implemented in spiking networks
   - Real-time map building while navigating

3. **Improved Vision**
   - Depth estimation in 3D
   - Binocular vision (potentially)

4. **Spatial Working Memory**
   - Navigation-based memory experiments
   - Continuous spatial representations

5. **Auditory System (In Progress)**
   - Verbal command interpretation
   - Replaces visual task cues

**The Arcade**
- Special environment with screen
- Allows running all SPAUN 2.0 experiments
- Bridging old and new capabilities
- Initially tried converting 2D tasks to 3D (didn't work - important lesson!)

> "So, initially we tried to take all of those experiments we did on the screen and translate them into 3D equivalents, but you cannot do that, right? which gives us a I think is very important to realize when you're doing those kinds of experiments that's what you're learning about right you're not necessarily learning what it would mean to then put that in the real world"

### 8. Human Spatial Memory Experiment Replication

**Original Experiment Design**
- 43-46 human subjects in virtual reality
- **MEG recordings** (magnetoencephalography) - direct cortical recordings
- Hippocampal data from humans (rare and valuable)

**Task Protocol**
1. Walk to chest, it opens showing item (e.g., hourglass)
2. Go to next chest, see different item (e.g., wooden logs)
3. Distractor task (shell game)
4. Query: "Do you remember where wooden logs are?"
5. Respond with confidence (yes/maybe/no)
6. Indicate location
7. Receive feedback (correct location shown)

**Human Performance Data**
- Accuracy measured across all subjects
- Accuracy as function of confidence level
- Hippocampal activity patterns (left vs. right hippocampus)
- Distinguished recalled vs. non-recalled objects vs. no-item conditions

**SPAUN 3.0 Replication**

*Behavioral Matching*:
- Model walks through environment viewing chests
- Builds internal spatial map with object locations
- Can be queried about object locations
- Accuracy varies with number of grid points used for decoding

*Neural Activity*:
- Entorhinal cortex: Grid cells tracking "where am I?"
- CA2 region: Bursts when encountering new objects
- Activity patterns comparable to human hippocampal recordings

> "uh we can also look at the activity in the hippocampus of the model part of the model uh and so here in entrano cortex this is basically doing all of the where am I right now right so this is all grid cells basically activity"

**Accuracy Calibration**
- With 50 grid points: Superhuman performance (nearly 100%)
- With fewer grid points: Matches human ~70-80% accuracy
- **Hypothesis**: Humans have limited sampling resolution for spatial decoding
- Shows how implementation constraints affect behavior

> "And you you know in so doing you can find basic you can find one particular or there's a range of values but you know some values which give you a pretty good match to the accuracy behavioral accuracy that you find in humans"

### 9. Hippocampal Cell Types in SPAUN 3.0

**Grid Cells**
- Fire in hexagonal grid pattern as agent moves
- Multiple scales of grids
- Become better defined over time
- Located in entorhinal cortex

**Place Cells**
- Fire when agent in specific location
- Location-specific activity
- Found throughout hippocampus

**Object Vector Cells**
- Fire when agent has consistent egocentric relation to object
- Encode object locations relative to self
- Important for object-location binding

**Time Cells**
- Encode temporal information
- Enable retrospective and prospective timing
- Critical for continuous time representation

> "So you can see things like grid cells, right? And you can see over more time the grid cells become better defined. You have things like object vector cells. So these X's are where objects were and you can see uh cells that are sort of firing whenever the agent is within some consistent egocentric relation to the object"

### 10. Neurosymbolic LLM Integration - Solving Math Reasoning

**The Problem**
- LLMs bad at algorithmic reasoning (math problems)
- SPAUN can execute step-by-step algorithms via basal ganglia
- VSAs provide structured representations for discrete problems

**The Solution: Hybrid Architecture**

1. **Input**: Math problem sentence (e.g., "What is 910 mod 213?")
2. **LLM Encoding**: Process into internal representation
3. **VSA Translation**: Convert to structured VSA representation
   ```
   First_number ⊛ (hundreds ⊛ 9 + tens ⊛ 1 + ones ⊛ 0)
   Second_number ⊛ (hundreds ⊛ 2 + tens ⊛ 1 + ones ⊛ 3)
   Operator ⊛ modulo
   ```
4. **Algorithm Execution**: Step-by-step solution using VSA operations
5. **Back to LLM**: Inject result back into LLM representation
6. **Output**: LLM generates answer

> "So basically taught it how to turn that its representation here into this representation. Uh then executed the algorithm that we know will solve the problem, generate a representation that we could then stick back into the language model"

**Binding Operator (⊛)**
- VSA operation that associates slot with filler
- "Hundreds digit is bound to 9"
- Enables structured, compositional representations

**Results: Massive Performance Gains**

Baseline comparisons:
- **Standard LLM** (orange): Poor performance on most tasks
- **LoRA fine-tuned** (red): Better on some, worse on others
- **Chain-of-thought** (green): Inconsistent improvements
- **Neurosymbolic** (blue): Dominant across almost all tasks

Specific improvements:
- **73% higher absolute accuracy** on average
- Bitwise XOR: 5% → 90% (85 percentage point gain!)
- Modular arithmetic: Dramatic improvements
- Preserves performance on tasks LLM already does well (addition, division)

> "Um and so to me this is the kind of thing that where you know what we did was basically take this bio inpired type of representation introduce it into a language model and get a massive improve improvement in reasoning on particular task types"

**Key Design Decision**
- Tasks LLM already does well: No intervention
- Algorithmic tasks: Route through VSA+algorithm
- Doesn't hurt existing capabilities

### 11. Two-Way Street: AI ↔ Neuroscience

**AI → Neuroscience**

*Surprising Impact of Scale*:
- Data-driven methods at massive scale produce unexpected capabilities
- LLMs demonstrate what's possible with scale

*Useful Starting Points*:
- Deep learning models as starting points for bioplausible models
- Best visual cortex models are deep learned networks
- Can retrofit biological constraints onto functional systems

> "right now I think our best models of the visual system are basically deeple learned models right uh so you we definitely have exploited that kind of thing in neuroscience"

**Neuroscience → AI**

*Bioinspired Architectural Constraints*:
- Basal ganglia action selection for task coordination
- Hierarchical organization of processing
- Separation of perception, cognition, and motor control

*Representational Innovations*:
- Vector symbolic architectures (VSAs)
- Continuous space/time representations
- Structured compositional semantics

*Surprising Efficacy*:
- State space models (from time cells)
- Neurosymbolic reasoning (from VSAs)
- More efficient than pure learning approaches

> "often have surprising efficacy of bioinspired either architectural or representational constraints right so uh so state space models are one example of that"

### 12. Future Development Roadmap

**In Progress**

1. **Temporal Working Memory**
   - Capture temporal distances between items
   - Not just order, but duration information

2. **Auditory System**
   - Interpret verbal commands
   - Replace visual task cues (A1, A5, etc.)
   - More natural for embodied agent

3. **Path Planning**
   - Current: Told where to go (like human experiment)
   - Future: Plan own paths for foraging tasks

4. **Second Camera**
   - Improved depth estimation
   - May not be necessary (working okay with one)

**Under Consideration**

1. **Amygdala Models**
   - Emotional processing
   - Fear conditioning
   - Affective influences on behavior

2. **Long-term Memory Improvements**
   - Beyond working memory
   - Episodic memory consolidation

**Open Questions**
- What additions would be most compelling?
- Eliasmith seeks community input on priorities
- Balance between complexity and scientific value

> "So, these are questions in our minds, right? So, I'm always happy to hear people's opinions about what would be the most compelling things to add into a model like this"

---

## Technical Deep Dives

### Neural Compiler Workflow

```
High-Level Function (Differential Equation)
         ↓
    [NEF Principles]
         ↓
  Representation: High-dimensional vectors
  Computation: Nonlinear transforms
  Dynamics: Neural time constants
         ↓
Spiking Neural Network
         ↓
  Biologically Plausible Implementation
```

### VSA Math Problem Encoding

**Problem**: "What is 910 mod 213?"

**VSA Representation**:
```
Problem =
  first_number ⊛ (100s⊛9 + 10s⊛1 + 1s⊛0) +
  second_number ⊛ (100s⊛2 + 10s⊛1 + 1s⊛3) +
  operator ⊛ mod
```

**Properties**:
- Compositional structure
- Each component can be extracted via unbinding
- Supports algorithmic manipulation
- Compatible with neural implementation

### Basal Ganglia Action Selection

**Role**: Information flow controller

**Function**:
- Monitors all cortical states
- Gates information into working memory
- Controls reward evaluation
- Manages decoding and output
- Coordinates task switching

**Size**: Relatively small portion of model
**Impact**: Essential for multitask coordination

> "it's kind of controll controlling information flow uh in order to perform those tasks. Uh and it itself is actually not a particularly large part of the model, but it's playing this uh fairly essential role"

---

## Key Experimental Validations

### 1. Visual System (V1)
- Classification over ~1000 categories
- Increased sparsification over processing layers
- Timing analysis matches monkey IT cortex recordings
- Analysis on spike trains (not weights) - apples-to-apples comparison

### 2. Bandit Task (Reinforcement Learning)
- Model learns reward probabilities over time
- Ventral striatum dynamics match rodent recordings
- Delay, approach, reward, return segments identified
- Spike raster plots comparable

### 3. Raven's Progressive Matrices
- Fluid intelligence test
- Pattern recognition and completion
- Subset accuracy matches college-educated humans
- True generalization (never seen problems before)

### 4. Mental Gymnastics (Instruction Following)
- Example: V + rotated B with back erased = heart
- Combines: pattern finding, question answering, pattern application
- Manipulates internal representations
- Multi-step reasoning

### 5. Spatial Navigation (SPAUN 3.0)
- Replicates human VR experiment
- Behavioral accuracy matches human data
- Hippocampal activity patterns comparable to MEG recordings
- Grid cells, place cells, object vector cells all present

---

## Theoretical Contributions

### 1. Continuous Representations Framework
- Extends VSAs from discrete to continuous domains
- Unified theory for language and spatial representations
- Explains emergence of hippocampal cell types
- Enables temporal duration encoding

### 2. State Space Models
- First published 2018-2019 from Eliasmith lab
- Biological origin (time cells) led to AI innovation
- More efficient than transformers
- Now standard in modern AI research

### 3. Neurosymbolic Integration
- Demonstrates how to combine neural and symbolic processing
- Shows 73% accuracy improvements on algorithmic tasks
- Preserves existing LLM capabilities
- Provides blueprint for hybrid architectures

### 4. Inductive Biases from Biology
- Sample efficiency through appropriate priors
- Structured representations for compositional reasoning
- Procedural execution through basal ganglia
- Continuous representations for spatiotemporal tasks

---

## Scale and Complexity

**SPAUN 2.0**
- 6 million neurons
- 20 billion connections
- 12 cognitive tasks
- 4 neurotransmitter types
- Largest recurrent neural network

**Human Brain**
- 86 billion neurons
- 100 trillion synapses
- SPAUN 2.0 is **80,000× smaller**

**SPAUN 3.0 Goals**
- Scale up toward billions of neurons
- Trillions of connections
- Full embodiment
- Rich environmental interaction

---

## Critical Insights

### 1. Discrete vs. Continuous Representations

**Not Either/Or, But Both**
- Language requires discrete slots
- Navigation requires continuous space
- Real intelligence needs both
- VSAs provide unified framework

### 2. Temporal Richness of Memory

**Standard Tests Underestimate Capability**
- Testing only order misses duration information
- Human memory is fundamentally temporal
- Models should capture full temporal structure
- Explains additional richness of biological memory

### 3. Implementation Constraints Matter

**Superhuman → Human Performance**
- More grid points = better spatial memory
- Reducing sampling resolution matches human accuracy
- Hardware constraints may explain behavioral limitations
- Not just algorithmic, but implementation-level theories needed

### 4. 2D → 3D Is Not Trivial

**Screen Tasks ≠ Embodied Tasks**
- Can't directly translate screen experiments to 3D
- Embodiment fundamentally changes the task
- Important methodological lesson
- What we learn is constrained by experimental setup

### 5. Biology-AI Synergy Is Bidirectional

**Circular Knowledge Flow**
- Brain models → algorithms (state space models)
- Algorithms → AI systems (transformers alternative)
- AI systems → neuroscience (vision models)
- Neuroscience → brain models (validation data)

### 6. Functional + Biological = Powerful

**Beyond Either Approach Alone**
- Pure functional AI: Limited by missing principles
- Pure biological models: Often non-functional
- Combination: Functional AND biologically valid
- Enables both AI advances and neuroscience discoveries

---

## Notable Quotes

> "if you're essentially representing things over a continuous space then you can think of a probability density function as a kind of continuous representation of uncertainty"

> "maps is something that brains are particularly good at. Uh and we know we've always been working on this if people have heard about place cells grid cells and so on in the hypocampus"

> "So what we're essentially doing is we're kind of going in and saying you know once you know that this is an algorithmic type problem math problem to solve you just represent the input in the right way you execute the algorithm on it and then it gives you the right answer"

> "It's 80,000 times smaller than a human brain, right? So it's kind of tiny in some ways"

> "one of the things we want to do in spawn 3 is all of the stuff that spawn 2 did plus more, right? Like we don't want we don't want to kind of lose any of the skill set"

> "uh right and these are from biology right so this is as I was saying before like you know one connection between AI and biology in my mind is basically state space models right that's where they came out of looking at how time cells can be modeled in the brain"

---

## Research Methodology

### Multi-Level Validation Strategy

**1. Single Cell Level**
- Spike timing analysis
- Cell type identification (grid, place, object-vector)
- Tuning curves
- Firing patterns

**2. Circuit Level**
- Population dynamics
- Connectivity patterns
- Neurotransmitter types
- Anatomical mappings

**3. Systems Level**
- Multi-region interactions
- Information flow
- Task-dependent coordination

**4. Behavioral Level**
- Task accuracy
- Reaction times
- Error patterns
- Learning curves

**5. Computational Level**
- Algorithms implemented
- Representations used
- Transform calculations
- Optimization principles

### Experimental Replication Approach

1. Find human/animal experiment with rich data
2. Implement same task in model
3. Match input/output modalities
4. Compare behavioral performance
5. Compare neural recordings
6. Use identical analysis methods
7. Iterate to improve match

---

## Applications and Impact

### Neuroscience Research
- Safe testing of interventions impossible in humans
- Hypothesis generation for mechanisms
- Understanding cognitive architecture
- Explaining hippocampal representations

### AI Development
- Novel architectures (state space models)
- Improved reasoning (neurosymbolic)
- Sample efficiency through inductive biases
- Multi-task learning frameworks

### Clinical Applications
- Understanding memory disorders
- Drug effect modeling
- Personalized brain models (digital twins)
- Neural prosthetics

### Robotics
- Low-power embodied AI
- Navigation systems
- Continuous learning
- Multi-modal integration

---

## Open Questions and Future Research

### Technical Questions

1. **How far can VSAs scale?** Can they handle complexity of full language?

2. **What's the optimal model size?** Balance between scale and efficiency?

3. **How to integrate full LLM?** State-based models in SPAUN 3.0?

4. **Path planning implementation?** What algorithm, which brain region?

5. **Amygdala integration?** How do emotions affect cognitive control?

### Scientific Questions

1. **Why are humans "bad" at spatial memory?** Is it sampling resolution or something else?

2. **How do time cells emerge?** What learning rule produces them?

3. **What determines inductive biases?** Can we systematically derive them from biology?

4. **How does brain balance discrete and continuous?** What's the neural mechanism for switching?

### Methodological Questions

1. **What should be added next?** Community input needed on priorities

2. **How to validate 3D embodiment?** What experiments are most informative?

3. **Should individual differences be modeled?** Or focus on canonical architecture?

4. **How to handle development?** Model learning from scratch vs. pre-trained?

---

## Conclusion

Chris Eliasmith's SPAUN 3.0 represents a paradigm shift in brain modeling: moving from disembodied, discrete-only systems to fully embodied agents with both discrete (language-like) and continuous (spatial-temporal) representations. The key innovations are:

1. **Vector Symbolic Architectures** extended to continuous domains
2. **State Space Models** enabling efficient temporal processing
3. **Neurosymbolic integration** dramatically improving LLM reasoning
4. **3D embodiment** with navigation and spatial memory
5. **Multi-level validation** from cells to behavior

Most importantly, SPAUN demonstrates a **bidirectional research strategy**: brain insights improve AI (state space models, VSAs), while AI techniques improve brain models (deep learning vision, language models). This circular knowledge flow accelerates both neuroscience understanding and AI capabilities.

The neurosymbolic LLM results (73% accuracy improvement) suggest that biological constraints are not limitations but **design principles** that enable capabilities current AI lacks. By understanding how brains solve problems like precise reasoning and sample-efficient learning, we can build AI that is both more capable and more efficient.

SPAUN 3.0 is not just a brain model—it's a research platform for discovering computational principles of intelligence. At 80,000× smaller than a human brain, it already demonstrates complex cognition, navigation, and reasoning. Scaling up while maintaining biological fidelity may reveal principles that transform both our understanding of intelligence and our ability to create it artificially.