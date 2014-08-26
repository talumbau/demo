## Prerequisites

### Blaze and Bokeh

`conda install blaze=0.6.1 bokeh=0.5.1`

## Configuration

Set the `EMP_DATA_DIR` environment variable to the path containing the employment dataset.

## Running the Demo

```
python preprocess.py
bokeh-server
python employment_vis.py
```
