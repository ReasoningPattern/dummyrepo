# How Do Large Reasoning Models Think? A First Look at Reasoning Behaviors in Code Generation

---

**Datasets:** In this study, we use the CoderEval dataset which can be found [here](https://github.com/CoderEval/CoderEval).

**Annotation:** The complete annotatation of each file could be found in the `Annotations` folder.

**Dataset Split:** The breakdown of the dataset split for the taxonomy construction and evaluation can be found in the `Artefacts/Taxonomy Construction Split` folder.


**Experimental Results:**  The experimental results are shown in the `Artefacts/Results` folder, with each folder corresponds with different versions listed on the paper. 

**Rule Mining Results:** The output of the association rule mining algorithm for Section 4.3 are shown in `Artefacts/Pattern Mining` folder.

---

**Set-Up:** Before starting the following process, it's essential to set up your environment by installing the necessary dependencies listed in the `requirements.txt` file. To install these dependencies, activate your Python virtual environment and run:

```bash
pip install -r requirements.txt
```


## Experiment

In order to run the experiments, run one of the python code corresponding to the model such as 'vllm_python_deepseek.py'

To modify the prompt input, modify the following code:

```bash
prompt_template = """
You are a Python software engineer.

Generate Python code based on the following function signature and docstring. 
Do NOT include any explanation, reasoning, or markdown formatting. 
Let’s think step by step, first try to recall previous knowledge you have on this matter, 
then construct the control flow, consider potential edge cases, finally make sure that the output code is correct.
Output ONLY the code generated, in python markdown format.

{input}

"""
```
## Testing

In order to compute the pass@k result, download the docker file from the CoderEval [repo](https://github.com/CoderEval/CoderEval).

Navigate to "/home/travis/builds/repos", copy the output jsonl file within the docker, reset the environment variable with:
```bash
python GroundTruth.py
```
Finally, run the experiment
```bash
python PythonExec.py <YOUR JSONL FILE NAME> 1
```
