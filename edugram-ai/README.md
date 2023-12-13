# Training the EduGram Classifier

For this I fine-tuned OpenAI's GPT-3 1B model.

Why? For convenience and time reasons.

I don't recommend actually using it in scale. Due to it's cost.

You can rather train a token classifier on your own, and it'll be much more cheaper.

# Dataset

The dataset I used was for a previous project I made for TikTok.

Where I got it from? I labeled the data by hand... Yeah.

In label_data.csv.
- Video ID, Description, Transcription

Which evenually turns into training_data_prepared.jsonl in the step below as the data that's going to be fine-tuned with.

# Prepping dataset
Mostly just data-preprocessing for the AI to actually process properly.

Steps are in prepping_fine_tune.ipynb.

# Training
I went on openai to run the fine-tune with this file.

These were the results:
![Alt text](image.png)