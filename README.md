# Training Material | Addfor S.p.A.

The following IPython Notebooks are the standard training material distributed with the Addfor trainings. For more information about standard and custom training solutions please visit [Training @ Addfor](https://www.add-for.com/training/).

All the IPython notebooks are distributed under the Creative Commons Attribution-ShareAlike 4.0 International License.

## Installation instructions

We recommend to install the Anaconda distribution to the latest version: please visit [continuum.io](https://www.continuum.io/downloads) to download Anaconda. The tutorials works with python3 (python2 is no longer supported). Next update the distribution to the latest release: `conda update anaconda`.

Clone this repository with git; use this command: `git clone --depth 1 https://github.com/addfor/tutorials` if you want to download only the current commit (faster, takes less disk space):

> Create a shallow clone with a history truncated to the specified number of commits.

Next cd into tutorials and create the environment addfor_tutorials from the file `addfor_tutorials.yml` (make sure the file is in your directory). Issue the command `conda env create -f addfor_tutorials.yml` (the process could take few minutes). After the installation is finished, activate the environment:

> Windows: `activate myenv`
> macOS and Linux: `source activate myenv`

All notebooks use our Addutils library: please install [Addutils](https://www.dropbox.com/s/g2vibmklfn2smz3/AddUtils-0.5.4-py34.zip) (for python3) before running the Notebooks. Download the zip file and open the Terminal or Anaconda Prompt: `source activate addfor_tutorials` if environment is not already active, then type `pip install AddUtils-0.5.4-py34.zip` (it should work for python3.4+).

At this point you are able to run the notebook with: `jupyter-notebook` and navigate through the directory tree.

**Note**: the first time you run the notebooks you could experience a brief slowdown due to matplotlib building its font cache. It should disappear the next session.

For more informations visit: [Download training material guidelines @ Addfor](https://www.add-for.com/downloads-tutorials/)

## Index

1. **Python + IPython/Jupyter**
    1. [An introduction to the IPython notebook](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py01v04_ipython_notebook_introduction.ipynb)
    1. [Python Basic Concepts](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py02v04_python_basics.ipynb)
    1. [Python Getting Started](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py03v04_python_getting_started.ipynb)
    1. [Python Style Guide](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py04v04_python_style_guide.ipynb)
    1. [Python More Examples](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py05v04_python_more_examples.ipynb)
    1. [Object Oriented Programming in Python](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py06v04_python_object_oriented.ipynb)
    1. [Integration of Python with compiled languages](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py07v04_python_speed-up_with_C.ipynb)
    1. [Unicode](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py08v04_Unicode.ipynb)
    1. [Regular Expressions](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/python-ipython/py09v04_python_regular_expressions.ipynb)
1. **NumPy**
    1. [Numpy Basic Concepts](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np01v04_numpy_basics.ipynb)
    1. [PyTables](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np02v04_numpy_PyTables.ipynb)
    1. [Numpy - Plotting with Matplotlib](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np03v04_numpy_plotting.ipynb)
    1. [Scipy - Optimization](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np04v04_scipy_optimization.ipynb)
    1. [Scipy Signal Processing: IIR Filter Design](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np05v04_scipy_sig_processing_IIRfilter_design.ipynb)
    1. [Symbolic Computation](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/numpy/np06v04_Symbolic_Computation.ipynb)
1. **Pandas**
    1. [pandas Dataframe - Basic Operativity](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd01v04_basic_data_operativity.ipynb)
    1. [pandas I/O tools and examples](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd02v04_input_output.ipynb)
    1. [Pandas Time series](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd03v04_time_series.ipynb)
    1. [Statistical tools](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd04v04_statistical_tools.ipynb)
    1. [Merge and pivot](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd05v04_data_organization.ipynb)
    1. [Split apply and combine](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd06v04_advanced_data_management.ipynb)
    1. [Sources of Open Data](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd07v04_open_data.ipynb)
    1. [Baby Names](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/pandas/pd08v04_babynames.ipynb)
1. **Machine learning**
    1. [Definitions and Advices](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml00v04_definitions.ipynb)
    1. [Prepare the Data](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml01v04_prepare_the_data.ipynb)
    1. [The scikit-learn interface](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml02v04_the_scikit-learn_interface.ipynb)
    1. [Visualizing the Data](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml03v04_visualizing_the_data.ipynb)
    1. [Dealing with Bias and Variance](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml04v04_dealing_with_bias_and_variance.ipynb)
    1. [Ensemble Methods](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml05v04_ensemble_methods.ipynb)
    1. [Ensemble Methods Advanced](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml06v04_ensemble_methods_advanced.ipynb)
    1. [Support vector machines (SVMs)](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml13v04_support_vector_machines.ipynb)
    1. [Predict Temporal Series](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml15v04_predict_temporal_series.ipynb)
    1. [Forecasting with LSTM](http://nbviewer.jupyter.org/github/addfor/tutorials/blob/master/machine_learning/ml16v04_forecasting_with_LSTM.ipynb)
    1. [Prognostics using Autoencoder](http://nbviewer.jupyter.org/github/addfor/tutorials/blob/master/machine_learning/ml17v04_prognostics_using_autoencoder.ipynb)
    1. [Theano Basic Concepts](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml20v04_theano_basics.ipynb)
    1. [Explore Neural Network Hyperparameters with Theano and Keras](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml21v04_theano_NN_explore_hyperparameters.ipynb)
    1. [Neural Networks with Nervana Neon library](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml23v04_neon_NN_basics_and_hyperparameters-py27.ipynb)
    1. [Tensorflow Basic concepts](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml25v04_tensorflow_basics.ipynb)
    1. [Explore Neural Network Hyperparameters with TensorFlow](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml26v04_tensorflow_NN_explore_hyperparameters.ipynb)
    1. [TensorFlow for beginners](http://nbviewer.jupyter.org/github/addfor/tutorials/blob/master/machine_learning/ml27v04_tensorflow_for_beginners.ipynb)
    1. [Keras - Theano Benchmark](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml30v04_Keras_NN_test.ipynb)
    1. [Neon Benchmark](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml31v04_Neon_NN_test-py27.ipynb)
    1. [TensorFlow Benchmark](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml32v04_TensorFlow_NN_test.ipynb)
    1. [Neural Network Benchmark Summary](http://nbviewer.ipython.org/github/addfor/tutorials/blob/master/machine_learning/ml33v04_NN_benchmark.ipynb)
