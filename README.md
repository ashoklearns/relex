# RELEX - Test Automation Framework  

**REL**iable **EX**ecution (**RELEX**) is a powerful test automation framework designed for **Command Line Interface (CLI) testing**. It emphasizes **ease of automation**, **stable regression**, and **seamless debugging**.  

---

## 🚀 Why Choose RELEX?  

### 🔄 Dynamic Device Selection  
Imagine running 10 scripts in regression, but the device goes down after script #5 due to a bug. Normally, the remaining 5 tests would fail simply because the device is unreachable.  
With **RELEX**, another device matching the criteria from the parameter file is automatically selected. This ensures you still get results for **9 out of 10 tests**, minimizing wasted runs.  

### 🧹 Efficient Cleanup  
Integration often fails due to improper cleanup from previous test runs.  
**RELEX** introduces a **STEP + CLEAN** approach, ensuring every configuration step has a corresponding cleanup step. This eliminates residue issues and stabilizes your regression pipeline.  

### 🐞 Pause & Debug Anytime  
Need to debug in the middle of a run?  
With **RELEX**, you can drop into **interpreter mode** at any point in your script. You can even validate entire new scripts interactively before adding them to regression. This drastically reduces debugging time.  

### 📊 Multi-Test Approach  
Matrix-style test cases often share common steps but differ in a few variations.  
**RELEX** supports a **setup function** where shared steps run once, while test-specific steps are isolated in their respective test cases. This reduces duplication and improves maintainability.  

### 🧩 Function-Based Script Design  
Scripts in **RELEX** are created as **sets of reusable functions**.  
If two different Devices Under Test (DUTs) share similar functionality, the same script can be reused by simply creating DUT-specific function definitions.  
This approach makes it:  
- Easy to **organize** automation scripts  
- Simple to **reuse and extend** across multiple DUTs  
- Maintainable in the long run, reducing code duplication

### 📜 Transparent Logging  
Stay in control with **real-time console logs** and **detailed log files**. At the end of execution, a clear **summary report** highlights key results, saving you from manual log digging.  

---

## ✨ Key Benefits  

- Stable and resilient regression runs  
- Cleaner automation with enforced cleanup  
- Interactive debugging on the fly  
- Optimized multi-test execution
- Function-based scripting for reuse and maintainability
- Clear and transparent reporting  

---

## 📖 Getting Started  

_Coming soon: installation and usage examples._  
