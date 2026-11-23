from collections import Counter
import statistics as st
import random
import os
import psycopg2

# Shirt colour for each day

week = {
    "MONDAY": ["GREEN", "YELLOW", "GREEN", "BROWN", "BLUE", "PINK", "BLUE", "YELLOW", "ORANGE", "CREAM", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "BLUE", "BLUE", "BLUE", "GREEN"],
    "TUESDAY": ["ARSH", "BROWN", "GREEN", "BROWN", "BLUE", "BLUE", "BLUE", "PINK", "PINK", "ORANGE", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "WHITE", "BLUE", "BLUE", "BLUE"],
    "WEDNESDAY": ["GREEN", "YELLOW", "GREEN", "BROWN", "BLUE", "PINK", "RED", "YELLOW", "ORANGE", "RED", "ORANGE", "RED", "BLUE", "BLUE", "WHITE", "BLUE", "BLUE", "WHITE", "WHITE"],
    "THURSDAY": ["BLUE", "BLUE", "GREEN", "WHITE", "BLUE", "BROWN", "PINK", "YELLOW", "ORANGE", "CREAM", "ORANGE", "RED", "WHITE", "BLUE", "WHITE", "BLUE", "BLUE", "BLUE", "GREEN"],
    "FRIDAY": ["GREEN", "WHITE", "GREEN", "BROWN", "BLUE", "BLUE", "BLACK", "WHITE", "ORANGE", "RED", "RED", "RED", "WHITE", "BLUE", "WHITE", "BLUE", "BLUE", "BLUE", "WHITE"],
}

# Flatten all days into one list and count each color
all_colours = [colour for day in week.values() for colour in day]
counts = Counter(all_colours)
freqs = list(counts.values())

# 1. Mean color: the color whose count is closest to the average count
mean_count = st.mean(freqs)
smallest_gap = min(abs(n - mean_count) for n in freqs)
mean_colors = [c for c, n in counts.items() if abs(n - mean_count) == smallest_gap]

# 2. Most worn color (mode)
top_count = max(freqs)
mode_colors = [c for c, n in counts.items() if n == top_count]

# 3. Median color: sort colors by count (then name), take the middle one(s)
ordered = sorted(counts, key=lambda c: (counts[c], c))
mid = len(ordered) // 2
median_colors = [ordered[mid]] if len(ordered) % 2 else ordered[mid - 1:mid + 1]

# 4. BONUS: variance of the counts
pop_variance = st.pvariance(freqs)    # whole group
sample_variance = st.variance(freqs)  # if treated as a sample

# 5. Probability that a random colour is RED

total = sum(counts.values())
p_red = counts.get("RED", 0) / total

# Result outputs (1-5) 

print(f"Counts: {dict(counts)}")
print(f"Mean count: {mean_count:.2f}")
print(f"1. Mean color(s):  {mean_colors}")
print(f"2. Most worn color: {mode_colors} ({top_count} times)")
print(f"3. Median color(s): {median_colors}")
print(f"4. Variance: population = {pop_variance:.3f}, sample = {sample_variance:.3f}")
print(f"""5. Probability that a random color chosen is RED: 
Red appears {counts.get('RED', 0)} times out of {total} shirts 
P(red) = {p_red:.4f} ({p_red:.2%})""")

# 6. BONUS: save colours and frequencies in PostgreSQL

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="shirts_db",
    user="postgres",
    password=os.environ.get("PGPASSWORD", "your_password"),
)

try:
    with conn:           # commits on success, rolls back on error
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS shirt_colours (
                    colour    VARCHAR(50) PRIMARY KEY,
                    frequency INTEGER NOT NULL
                );
            """)

            # Upsert, so rerunning the script doesn't create duplicates
            cur.executemany("""
                INSERT INTO shirt_colours (colour, frequency)
                VALUES (%s, %s)
                ON CONFLICT (colour) DO UPDATE SET frequency = EXCLUDED.frequency;
            """, list(counts.items()))

            # Verify what was saved
            cur.execute("SELECT colour, frequency FROM shirt_colours ORDER BY frequency DESC;")
            for colour, freq in cur.fetchall():
                print(colour, freq)
finally:
    conn.close()

# 7. BONUS: Recursive search

def recursive_search(numbers, target, index=0):
    # Base case 1: reached the end without finding it
    if index == len(numbers):
        return -1
    # Base case 2: found it
    if numbers[index] == target:
        return index
    # Recursive case: check the next position
    return recursive_search(numbers, target, index + 1)

print("\n7. Recursive search")
numbers = [4, 8, 15, 16, 23, 42]
target = int(input("Enter a number to search for: "))

result = recursive_search(numbers, target)
if result != -1:
    print(f"{target} found at index {result}")
else:
    print(f"{target} not found in the list")

# 8. Random 4-digit binary number to base 10

print("\n8. Random 4-digit binary number to base 10")

# Generate a 4-digit binary string, e.g. "1011"
binary = "".join(str(random.randint(0, 1)) for _ in range(4))
print("Binary number:", binary)

# Method 1: built-in
decimal = int(binary, 2)
print("Base 10 (built-in):", decimal)

# Method 2: manual (each digit is worth a power of 2)
decimal_manual = 0
for i, digit in enumerate(reversed(binary)):
    decimal_manual += int(digit) * (2 ** i)
print("Base 10 (manual):", decimal_manual)

# 9. Sum of first 50 Fibonacci numbers

a, b = 0, 1
total = 0

for _ in range(50):
    total += a
    a, b = b, a + b

print(f"\n9. Sum of the first 50 Fibonacci numbers: {total}")