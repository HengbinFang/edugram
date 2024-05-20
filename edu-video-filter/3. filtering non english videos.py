from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

# ONLY USING ENGLISH VIDEOS, BECAUSE THAT's WHAT THE AI WAS TRAINED ON

good = []
with open("new_data.txt", "r", encoding="utf-8", errors="ignore") as file:
    data = file.read().splitlines()
    for x in data:
        id, text = x.split("|||")
        if text:
            try:
                d = detect(text)
                if d == "en":
                    print("Appended!", d)
                    good.append(x)
                else:
                    print(d)
            except Exception as er:
                print("Error:", er)
                good.append(x)
        else:
            good.append(x)

with open("english_videos.txt", "a", encoding="utf-8") as file:
    file.write("\n".join(good))