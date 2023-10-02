# Tensorflow Songwriter

A one-shot Python songwriter using Tensorflow.

There are two programs:

1. vectorize-midi.py one-shot vectorizes all midi data stored in Pop_Music_Midi and outputs `midi_vectors.ann`. A `.ann` files store the vectors and the index for approximate nearest neighbor search.

2. train-model.py trains Tensorflow's Keras LSTM on this data and outputs a midi clip as generated_song.mid.
Open generated_song.mid in GarageBand to hear it.

Notes:

1. Currently uses annoy db, but Astra DB would probably be better when you throw more than a local folder of MIDI files at it. :-)
2. Instance.yaml and pipeline.yaml will deploy to Astra Streaming if you provide a secrets.yaml file.

To do: 

1. Use write-to-astra instead of annoy db
2. Train-model should retrieve vectors from astra
3. The current model is just counting when notes 0 - 128 are on or off, which makes the generated song one note, or one cluster of notes. Research to create richer results.
4. Stream midi to a local instrument port to scare the cat.

# Install and run
NOTE: 
This repo contains Pop_Music_Midi, a directory with MIDI material for training.

1. Clone this repo
2. CD to /Python. 
3. Create a virtual environment and build the project from requirements.txt:
```python
python3 -m venv vector-music
source vector-music/bin/activate
python3 -m pip install -r requirements.txt
```
4. Run program in the virtual environment:
```python
python3 vectorize-midi.py
python3 train-model.py
```
5. This will generate a `generated_song.mid` in /Python.

## Deploy to LangStream

[LangStream](https://github.com/LangStream) is a way to deploy, run, and scale AI applications in Kubernetes.
Here I'm using the LangStream CLI to deploy the application.
LangStream reads the instance, pipeline, and secrets YAML files from this root directory, and deploys the application.
In this case I tested with a minikube, and now I'm deploying to DataStax Astra with the current setup, but you can use your own K8s cluster, a local Docker, whatever you'd like!

```shell
langstream apps deploy vector-music \
-i ./instance.yaml \
-app ./python \
-s ./secrets.yaml`
```

Result:
```shell
packaging app: /Users/mendon.kissling/PycharmProjects/pythonProject/./python
app packaged
deploying application: vector-music (1901 KB)
application vector-music deployed
```
