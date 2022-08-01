# Backlog

- Determine best temperature value or see if varying it would be better
    - Could be a range of values too
    - example: .2 is better for k = 1, but .8 is better for k=100
    - so could use .2  for first 5 attemts and then make it larger over time
- split code into multiple files
- could create onnx/quantized/faster version of the models, put them on huggingface and then could dynamically call them from the code
- make it pip installable from github
- add a verbose mode to give updates on how many attempts have been tried