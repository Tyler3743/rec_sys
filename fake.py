from faker import Faker
import pandas as pd
import numpy as np
fake = Faker()
ratings=pd.read_csv('ratings.csv', usecols=['userId'])
users = sorted(ratings['userId'].unique())
users_df = pd.DataFrame({
    'id': users,
    'full_name': [fake.name() for _ in users],
    'gender': np.random.choice(['Male','Female'], size=len(users)),
    'email': [f'user{uid}@example.com' for uid in users],
    'birth_date': [fake.date_of_birth(minimum_age=14, maximum_age=70) for _ in users],
    'phone_number': [fake.phone_number() for _ in users],
})
users_df.to_csv('users.csv', index=False)
print(users_df.head())
