import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

df_detailed = pd.read_csv("detailed_jsearch_job_listings.csv")

print(df_detailed['job_title'].unique())

# average salary trend
avg_min_salary = df_detailed['job_min_salary'].mean()
avg_max_salary = df_detailed['job_max_salary'].mean()
print(f"Average min salary for Data Analysts: ${avg_min_salary:.2f}")
print(f"Average max salary for Data Analysts: ${avg_max_salary:.2f}")

plt.hist(df_detailed['job_min_salary'], bins=20, alpha=0.5, label='Min Salary')
plt.hist(df_detailed['job_max_salary'], bins=20, alpha=0.5, label='Max Salary')
plt.legend()
plt.xlabel('Salary')
plt.ylabel('Frequency')
plt.title('Salary Distribution for Data Analysts')
plt.show()

# Top 10 states with data analyst jobs
jobs_by_state = df_detailed['job_state'].value_counts().head(10)
sns.barplot(x=jobs_by_state.index, y=jobs_by_state.values)
plt.xticks(rotation=90)
plt.xlabel('State')
plt.ylabel('Number of Jobs')
plt.title('Data Analyst Jobs by State')
plt.show()

# Skills and tools from Job Description
skills = ['python', 'sql', 'tableau', 'excel', 'r', 'sas', 'spss', 'power bi', 'data visualization', 'machine learning']
skill_counts = Counter()

for desc in df_detailed['job_description']:
    for skill in skills:
        if re.search(skill, desc, re.IGNORECASE):
            skill_counts[skill] += 1

sns.barplot(x=list(skill_counts.keys()), y=list(skill_counts.values()))
plt.xticks(rotation=90)
plt.xlabel('Skill')
plt.ylabel('Frequency')
plt.title('Most In-Demand Skills for Data Analysts')
plt.show()

# Export top skills
pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count']).to_csv("top_skills_for_data_analysts.csv", index=False)

# Export salary analysis
salary_analysis = df_detailed[['job_title', 'job_min_salary', 'job_max_salary']]
salary_analysis.to_csv("data_analyst_salary_analysis.csv", index=False)

# Export top skills for data analysts
top_skills_df = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count'])
top_skills_df.to_csv("top_skills_for_data_analysts.csv", index=False)

