# MNIST and Learning Methods

Mohamed Barakat | October 23, 2026

This report explains self-supervised learning and how models learn offline or online. It then compares four MNIST neural network experiments recorded with MLflow on DagsHub. The baseline achieved the highest final validation accuracy among the tested configurations.

# Part A Self supervised learning

## How it works

Self-supervised learning trains a model using targets created from the data itself. A target is the answer the model tries to predict. Instead of asking a person to label every example, a training task hides, transforms, or separates part of the original data. The original information supplies a way to check the prediction. The model calculates its error and adjusts its internal weights to reduce that error.

For example, a system could hide a word in a sentence and predict it from the surrounding words. The hidden word is already in the original sentence, so a human does not need to write a new answer. Repeating this task across many sentences helps the model learn useful representations, meaning patterns that summarize relationships in the data. A pre-trained representation can later be adapted to a specific task using labelled examples.

## Difference from unsupervised learning

Unsupervised learning is a broad category of learning from data without externally supplied task labels. Common examples include clustering similar customers and finding a smaller set of features that describes a dataset. These methods aim to discover structure in the data. Self-supervised learning specifically constructs a prediction or matching task with targets derived from the observations. The categories overlap: self-supervised learning is often treated as a form of unsupervised representation learning, rather than a completely separate category.

For example, clustering news articles could reveal groups about sports, business, and politics without being told those names. A self-supervised text model could instead predict hidden words in the same articles. Both use unlabelled text, but their training tasks differ.

## Examples and uses

In language processing, BERT learns by predicting masked tokens using their surrounding context. Its learned language representations can then be fine-tuned for tasks such as answering questions and classifying text. This separates learning general language patterns from learning the labels of a particular application.

In computer vision, SimCLR creates two augmented views of the same image, for example through cropping and colour changes. It trains representations so views from the same original image are more similar than views from different images. The resulting features can support image classification after pre-training, reducing reliance on large quantities of manually labelled images.

Self-supervision is useful when raw text or images are plentiful and human labels are expensive. However, pre-training can require substantial computing resources. Its usefulness also depends on whether the constructed task teaches patterns relevant to the later application. A model can still learn unwanted biases or shortcuts from its training data.

# Part B Online and offline learning

## Offline learning

Offline learning trains a model using a collected dataset during a separate training stage. The trained model is then used to make predictions. Making a prediction does not automatically change its weights. To incorporate later data, a new training process is scheduled and the updated model is evaluated before replacing the earlier version. This makes it practical to compare model versions under controlled conditions.

For example, a house-price model could be trained on a snapshot of past sales, including location, floor area, and sale price. It then estimates prices for new houses using the relationships it learned. Recording more sales does not update the deployed model by itself. A later training job can use an updated dataset to produce another version.

Offline training is easier to reproduce when the dataset, preprocessing, settings, and random seed are recorded. It also gives time to inspect the model before deployment. Its limitations include the cost of retraining and the possibility that predictions become less useful as real-world patterns change. An older housing model may struggle after interest rates or local market conditions change.

## Online learning

Online learning updates a model incrementally as new examples or small batches become available. The model carries forward what it has already learned rather than starting from scratch for every update. Some scikit-learn estimators provide a partial_fit method for this kind of incremental training. Processing smaller batches can also support datasets that do not fit in memory all at once.

For example, an email filter could update from newly reviewed messages as users identify spam. A recommendation model could update from recent interactions so that it responds to changing interests. Updates in supervised systems still need useful feedback or labels; receiving a new observation alone does not necessarily provide its correct answer.

Online learning can adapt quickly, but it requires careful monitoring. Incorrect labels, unusual batches, or malicious inputs may influence the next version. Updates can also make the model forget older patterns. The learning rate controls the size of an update: overly large updates can make learning unstable, while very small updates may respond too slowly to change.

## Choosing and evaluating an approach

The choice depends on how quickly the data changes and how much control is needed over each release. Offline learning suits stable datasets and applications requiring thorough checks before deployment. Online learning suits changing data streams when reliable feedback and monitoring are available. A system can also combine periodic offline training with smaller incremental updates.

Online and offline describe the update process, not whether an internet connection is present. They also differ from supervised and self-supervised learning, which describe the source of the training signal. Training an offline neural network in mini-batches does not by itself make it an online production system. In this assignment, the MNIST dataset is fixed and each model is trained in a separate offline experiment. For time-dependent applications, evaluation should preserve time order and avoid using future information to predict earlier events.

# Part C MNIST experiments

## Data preparation and tracking

I used the saved results from four TensorFlow and Keras runs in the Assignment 3 MNIST experiment on DagsHub. MLflow TensorFlow autologging recorded epoch-level accuracy, validation accuracy, loss, validation loss, and model artifacts. The code also logged the number of hidden layers, nodes in each hidden layer, optimizer, batch size, and final summary metrics. The notebook verification checked all four runs, required parameters, recorded epoch histories, and saved model artifacts.

MNIST contains 28 by 28 grayscale digit images. Pixel values were converted to float32 and divided by 255. The original training set was divided into 48,000 training and 12,000 validation examples using a stratified split with random seed 42. All runs used that same split. The separate 10,000-example test set was reserved until after model selection.

Each model began with Flatten and ended with a ten-node softmax layer. Hidden Dense layers used ReLU. The loss was sparse categorical cross-entropy. The saved run used Python 3.11.9, TensorFlow 2.18.0, and MLflow 2.20.3 on the CPU.

## Experiment configurations

| **Run**  | **Hidden nodes** | **Optimizer** | **Learning rate** | **Batch** | **Epochs** |
|----------|------------------|---------------|-------------------|-----------|------------|
| Baseline | \[128\]          | Adam          | 0.001             | 64        | 50         |
| Wider    | \[256\]          | Adam          | 0.001             | 64        | 10         |
| Deeper   | \[128, 64\]      | Adam          | 0.001             | 64        | 10         |
| SGD      | \[128\]          | SGD           | 0.010             | 64        | 10         |

The SGD configuration used momentum 0.9. Run names were baseline_128_adam_b64_e50, wider_256_adam_b64_e10, deeper_128_64_adam_b64_e10, and sgd_128_b64_e10. The baseline followed the required 50-epoch settings. The additional runs used ten epochs each to reduce computation.

## Final epoch results

| **Run**  | **Training accuracy** | **Validation accuracy** | **Training loss** | **Validation loss** |
|----------|-----------------------|-------------------------|-------------------|---------------------|
| Baseline | 100.00%               | 97.925%                 | 0.000057          | 0.135785            |
| Wider    | 99.62%                | 97.542%                 | 0.013823          | 0.084961            |
| Deeper   | 99.46%                | 96.808%                 | 0.018472          | 0.123604            |
| SGD      | 98.27%                | 97.242%                 | 0.063013          | 0.096612            |

Accuracy is the fraction of correct digit predictions. Loss is the cross-entropy error calculated from predicted class probabilities; lower loss is better. Values above are rounded from the completed notebook output. Each row uses its final epoch rather than its best intermediate epoch.

# Model selection and project links

I selected baseline_128_adam_b64_e50 because it had the highest final validation accuracy, 97.925%, among the four tested configurations. The selection rule was highest final validation accuracy, with lower validation loss used only to break an exact accuracy tie. The baseline exceeded the wider model by about 0.383 percentage points. Its 100% training accuracy was not the reason for selecting it.

The wider model had the lowest validation loss, 0.084961, while the baseline had a higher validation loss of 0.135785. Therefore, the baseline was best under the chosen accuracy criterion, but did not lead on every metric. If the main objective were minimizing validation cross-entropy, the wider configuration would be preferred. The baseline also had a training-to-validation accuracy gap of approximately 2.1 percentage points, showing that perfect training accuracy did not transfer to the held-out examples.

These experiments compare complete configurations with different training budgets. The baseline trained for fifty epochs and the other models trained for ten, so the results do not isolate the effects of architecture or optimizer. One validation split and one random seed also do not establish that the ranking will hold for other splits or repeated runs. Those limitations should be considered when interpreting small score differences.

After choosing the baseline using validation performance, I evaluated its saved model on the untouched test set. Its test accuracy was 97.87% and test loss was 0.124895. The test score was not used to choose between the four runs.

## Project addresses

GitHub code repository  
https://github.com/dw733/assignment3-mnist

DagsHub repository  
https://dagshub.com/dw733/assignment3-mnist-mlflow

MLflow Tracking URI  
https://dagshub.com/dw733/assignment3-mnist-mlflow.mlflow

Selected MLflow run ID  
302cdcec36d54442ae5af288c46fe10a

# DagsHub baseline and completed runs



Figure 1 Completed baseline run with its parameters and metrics



Figure 2 Four completed runs with logged configurations in the order SGD deeper wider and baseline

# DagsHub comparison of four runs

The full comparison screenshot shows training and validation metrics for all four runs. Test metrics appear only for the selected baseline.



Figure 3 Full DagsHub comparison showing metrics and training curves

# DagsHub validation curves

The full chart screenshot shows validation accuracy and loss across epochs. Run names and configurations are listed in Part C.



Figure 4 Full DagsHub charts showing validation curves and selected model test metrics
