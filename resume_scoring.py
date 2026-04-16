import pandas as pd

# Sample candidate data
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Skills": ["Python, SQL, Excel", "Java, C++, SQL", "Python, Data Analysis"],
    "Experience_Years": [3, 5, 2]
}

df = pd.DataFrame(data)

# Job requirements
required_skills = ["Python", "SQL"]

# Scoring function
def score_candidate(skills, experience):
    score = 0
    for skill in required_skills:
        if skill in skills:
            score += 2
    score += experience
    return score

# Apply scoring
df["Score"] = df.apply(lambda x: score_candidate(x["Skills"], x["Experience_Years"]), axis=1)

# Sort candidates
df = df.sort_values(by="Score", ascending=False)

print(df)
