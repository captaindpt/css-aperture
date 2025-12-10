# "How to Build a Brain" - Neuromorphic Engineering Perspective

## TL;DR: This is NOT a neuromorphic computing book

You're looking for **neuromorphic engineering** (building brain-inspired hardware), but this book is **computational neuroscience** (simulating brains in software). Wrong domain.

## What This Book Actually Is

**Computational Neuroscience:**
- Software simulations of spiking neurons
- Nengo framework runs on CPUs/GPUs
- 2.5 hours to simulate 1 second of Spaun
- Consumes massive power (standard compute)
- Focus: Understanding brain computation through simulation

**NOT Neuromorphic Engineering:**
- Not about IC design
- Not about analog/digital hybrid circuits
- Not about memristors or novel devices
- Not about event-driven asynchronous hardware
- Not about power-efficient silicon implementations

## The Book's Token Neuromorphic References

### What They Actually Say:

> "The low-power high-efficiency computing necessary to run very large simulations in real time will most likely be realized through more direct hardware implementation."

Translation: "Our software is too slow, maybe someone else will build hardware for it."

> "Our lab is currently working in collaboration with these groups [SpiNNaker, Neurogrid] to simulate millions of neurons in real time. However, we are only beginning to address the many challenges that remain for implementing arbitrary SPA models in neuromorphic hardware."

Translation: "We're trying to port our models to actual neuromorphic hardware but it's hard and we haven't really done it."

### The Power Argument:

> "Brains consume only about 20 watts... [Roadrunner supercomputer] consumes 2.35 MW, which is about 100,000 times more power than the brain."

They acknowledge the power efficiency problem but their solution is **software simulation**, not hardware design. Their Spaun model running on traditional compute is closer to the supercomputer end of the spectrum.

## What You Actually Need for Neuromorphic Computing

### 1. **IC Design Fundamentals**
- CMOS circuit design
- Analog/mixed-signal design
- Low-power circuit techniques
- Layout and fabrication
- **Books:** Baker's "CMOS Circuit Design" or Razavi's "Design of Analog CMOS ICs"

### 2. **Neuromorphic-Specific Knowledge**
- Event-driven asynchronous circuits
- Address-event representation (AER)
- Analog neuron circuits (e.g., silicon neurons)
- Memristor/ReRAM technology
- Spike-based computing

### 3. **Real Neuromorphic Architectures**
**Intel Loihi 2 (2021):**
- 128 cores, up to 1M neurons per chip
- 8 million synapses per core
- Event-driven asynchronous
- 15-300 pJ per synaptic operation
- Programmable learning rules

**IBM TrueNorth (2014):**
- 4096 cores, 1M neurons, 256M synapses
- 70 mW at max load
- Event-driven with 1ms timesteps
- 26 pJ per synaptic event

**BrainScaleS-2 (2020):**
- Analog neuromorphic substrate
- 10,000x faster than biological real-time
- Mixed analog-digital design
- Sub-milliwatt per neuron

**SpiNNaker (mentioned in book):**
- Digital asynchronous design
- 1 million ARM cores
- Packet-switched event routing
- ~1W per chip (18 cores)

### 4. **Algorithm-Hardware Co-design**
This is the key insight you mentioned: **"IC Design alongside algorithm knowledge leads to hyper-optimized neural circuitry"**

**Examples:**
- **Eyeriss (MIT):** CNN accelerator with row-stationary dataflow optimized for energy efficiency
- **Cerebras WSE:** Wafer-scale engine where algorithm (sparse activation) meets extreme hardware parallelism
- **Google TPU:** Matrix multiplication optimized at the silicon level for transformers
- **Graphcore IPU:** Graph-based computation with algorithm-aware memory hierarchy

The key is understanding:
- What operations your algorithm actually does (matmul, convolution, sparse ops)
- How to map those to silicon efficiently
- Power/area/speed tradeoffs
- Memory hierarchy and data movement (often the bottleneck)

## Why This Book Doesn't Help You

### What the book gives you:
- ❌ No IC design
- ❌ No circuit schematics
- ❌ No hardware architecture discussion
- ❌ No analog design
- ❌ No power budgeting methodology
- ✅ Spiking neuron models (useful for simulation only)
- ✅ NEF framework (software, not hardware)
- ⚠️ Vague mentions of "we should use neuromorphic hardware someday"

### What you actually need:
- ✅ Understanding of CMOS physics and circuits
- ✅ Low-power design techniques
- ✅ Asynchronous/event-driven design
- ✅ Memory architectures (SRAM, ReRAM, memristors)
- ✅ Dataflow optimization
- ✅ Algorithm-hardware co-design methodology

## The Real Path to Neuromorphic Computing

### 1. **Hardware Foundation**
Start here:
- Digital IC design (Rabaey, Weste & Harris)
- Analog IC design (Razavi, Baker)
- Low-power techniques (Chandrakasan)
- VLSI design flows (Cadence, Synopsys tools)

### 2. **Neuromorphic-Specific Learning**
Then move to:
- Mead's "Analog VLSI and Neural Systems" (classic, 1989)
- Indiveri & Liu's "Neuromorphic Engineering" papers
- Intel Loihi documentation and SDK
- SpiNNaker architecture papers
- BrainScaleS analog neuron circuits

### 3. **Algorithm Understanding**
Know what you're implementing:
- SNNs (Spiking Neural Networks) - if going spike-based
- CNNs/Transformers - if building accelerators
- Sparse operations and their hardware implications
- Quantization and its circuit-level impacts

### 4. **Co-design Practice**
Learn the dance:
- Profile algorithms for compute/memory bottlenecks
- Design custom datapaths for dominant operations
- Optimize memory hierarchy for access patterns
- Consider power at every level (algorithm → architecture → circuit → layout)

## Modern Neuromorphic vs. AI Accelerators

**Two paths diverged:**

### Path 1: Brain-Inspired (True Neuromorphic)
- Event-driven spiking
- Asynchronous operation
- Ultra-low power (pJ per operation)
- Examples: Loihi, TrueNorth, SpiNNaker
- **Challenge:** Limited software ecosystem, different programming model

### Path 2: DNN Accelerators (Pragmatic)
- Synchronous operation
- Optimized for matmul/convolution
- Moderate power (better than GPU, not brain-level)
- Examples: TPU, Eyeriss, Cerebras, Graphcore
- **Advantage:** Works with existing deep learning frameworks

**The trend:** Path 2 is winning in industry because it's backward compatible with existing ML. Path 1 might win long-term if we figure out how to train large SNNs effectively.

## Books You Should Read Instead

### For Neuromorphic Hardware:
1. **"Neuromorphic Engineering: From Biological to Spike-Based Hardware Neural Networks"** - Indiveri et al.
2. **"Analog VLSI and Neural Systems"** - Carver Mead (old but foundational)
3. **Intel Loihi documentation** - Modern, practical neuromorphic
4. **"Efficient Processing of Deep Neural Networks"** - Sze, Chen, Yang (more accelerator-focused)

### For IC Design:
1. **"CMOS VLSI Design"** - Weste & Harris
2. **"Design of Analog CMOS Integrated Circuits"** - Razavi
3. **"Digital Integrated Circuits"** - Rabaey, Chandrakasan
4. **"Low Power Digital CMOS Design"** - Chandrakasan & Brodersen

### For Algorithm-Hardware Co-design:
1. **"Computer Architecture: A Quantitative Approach"** - Hennessy & Patterson
2. **"Efficient Processing of Deep Neural Networks"** - Sze, Chen, Yang, Emer
3. Papers from MIT's Eyeriss team, Google's TPU papers, Cerebras publications

## What to Actually Learn From This Book (If Anything)

If you must read it for neuromorphic context:

**Useful:**
- Chapter 2: Spiking neuron models (LIF neurons) - understand what you might implement in silicon
- Understanding that spike-based computation is event-driven (sparse in time)
- The power efficiency argument (brain = 20W, good motivation for neuromorphic)

**Skip:**
- Everything about Semantic Pointer Architecture (irrelevant to hardware)
- Circular convolution binding (software concept, doesn't map well to hardware)
- NEF framework (it's a software compiler, not hardware methodology)
- Most of the cognitive modeling (interesting but orthogonal to IC design)

## The Real Neuromorphic Challenge

**It's not about simulating neurons accurately.** It's about:

1. **Event-driven asynchronous design** - spikes are sparse, exploit that
2. **Local computation** - minimize data movement (it dominates power)
3. **In-memory computing** - put compute where data lives (memristors, etc.)
4. **Analog computation** - some operations cheaper in analog domain
5. **Algorithm co-design** - algorithms that exploit hardware, hardware that enables algorithms

## Final Verdict

**For neuromorphic computing: 2/10**
- Mentions neuromorphic hardware exists
- Gives motivation (brain power efficiency)
- Provides spiking neuron models you might implement
- But it's fundamentally a software simulation book, not hardware design

**What you should do instead:**
1. Get solid IC design foundation (digital + analog)
2. Study actual neuromorphic chips (Loihi papers, TrueNorth, SpiNNaker)
3. Learn about AI accelerators (TPU, Eyeriss) for comparison
4. Practice algorithm-hardware co-design on real problems
5. If you want spikes, learn SNNs properly (not from this book)
6. Build stuff: FPGA prototypes → tape out simple test chips

**Bottom line:** This book studies brains to understand cognition. You want to build chips inspired by brains to run efficiently. These are related but different goals. You need IC design chops + algorithm understanding, not computational neuroscience models.

Go learn circuit design and study actual neuromorphic chip papers instead.
