import pandas as pd
import os

def main():
    # Read the full CSV
    input_csv = os.path.join(os.path.dirname(__file__), '../processed/Exploration_Reports.csv')
    output_csv = os.path.join(os.path.dirname(__file__), '../processed/Exploration_Reports_1000.csv')
    
    # Read the full dataset
    df = pd.read_csv(input_csv)
    
    # Take first 1000 rows (including header = 1001 total lines)
    df_sample = df.head(1000)
    
    # Save to new CSV
    df_sample.to_csv(output_csv, index=False)
    print(f"1000-row sample CSV written to {output_csv}")
    print(f"Sample contains {len(df_sample)} rows")

if __name__ == "__main__":
    main() 