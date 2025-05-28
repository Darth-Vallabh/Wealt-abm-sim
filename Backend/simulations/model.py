import numpy as np
import pandas as pd
import random
from scipy.stats import truncnorm

# -----------------------------
# 1. Configuration
# -----------------------------

def default_config():
    return {
        "num_decile": 10,
        "wealth_per_decile": [100, 200, 300, 400, 500, 600, 1000, 1500, 3000, 15000],
        "birth_rate": [0.09, 0.08, 0.07, 0.065, 0.05, 0.048, 0.04, 0.03, 0.025, 0.02],
        "death_rate": [0.025, 0.02, 0.018, 0.014, 0.012, 0.011, 0.008, 0.007, 0.006, 0.005],
        "net_migration": [0.05, 0.04, 0.035, 0.0325, 0.025, 0.024, 0.02, 0.015, 0.011, 0.01],
        "rate_of_return": [0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16],
        "total_population": 1000,
        "savings_rate": [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8],
        "num_time_steps": 10,
        "inheritance_tax_rate": 0.2,
        "wealth_tax": 0.05,
        "cg_tax": 0.2,
        "state_collections": 0,
        "wage_band_low": [100, 200, 300, 400, 600, 800, 1200, 1600, 2000, 3000],
        "wage_band_high": [200, 300, 400, 600, 800, 1200, 1600, 2000, 3000, 10000],
        "unemployment_rate": [0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15]
    }


def initialize_wealth(num_agents, wealth_per_decile):

    agents_per_decile = num_agents // 10  # Equal distribution among deciles
    agent_data = []

    agent_id = 1
    for decile in range(10):  # Deciles are indexed from 0 to 9
        avg_wealth = wealth_per_decile[decile]
        age = random.randint(18, 100)

        for _ in range(agents_per_decile):
            agent_data.append([agent_id, decile + 1, avg_wealth, avg_wealth,age])
            agent_id += 1

    # Convert to DataFrame
    df = pd.DataFrame(agent_data, columns=["ID", "Decile", "Wealth", "Initial Wealth (T=0)", "Age"])
    return df

def update_population(df, birth_rate, death_rate, net_migration, wealth_per_decile, first_time_step=True):
  df = df.copy()

    # Reset Status for existing agents
  df['Status'] = 0

  # Track the maximum existing ID for new agent assignment
  max_id = int(df['ID'].max()) if not df.empty else 0
  new_agents = []
  decile_counts = df['Decile'].value_counts().to_dict()

  for decile in range(1, len(birth_rate) + 1):  # Iterate over deciles (1 to n)
      count = decile_counts.get(decile, 0)  # Get current count or 0 if no agents
    #  print(count, decile)

      # Calculate new births, deaths, and migrations
      births = int(count * birth_rate[decile - 1])
      deaths = int(count * death_rate[decile - 1])
      migration = int(count * net_migration[decile - 1])

  # Ensure population doesn't go negative
      new_count = max(count + births - deaths , 0)

       # Mark deaths
      if deaths > 0:
          dead_indices = df[df['Decile'] == decile].sample(n=min(deaths, count)).index
          df.loc[dead_indices, 'Status'] = 1  # Mark as dead

      # Mark migrations
      if migration > 0:
          migrated_indices = df[df['Decile'] == decile].sample(n=min(migration, count)).index
          df.loc[migrated_indices, 'Status'] = 2  # Mark as migrated

        # If we need to add more agents
      if births > 0:
          agents_to_add = new_count - count
          new_ids = range(max_id + 1, max_id + 1 + agents_to_add)

          # Sample wealth from existing agents if possible, otherwise use decile average
          if count > 0:
              sampled_wealth = np.random.choice(df[df['Decile'] == decile]['Wealth'], size=agents_to_add, replace=True)
          else:
              sampled_wealth = [wealth_per_decile[decile - 1]] * agents_to_add  # Use decile wealth if no agents exist

          # Set initial wealth correctly
          if first_time_step:
              initial_wealth = [wealth_per_decile[decile - 1]] * agents_to_add
          else:
              if (decile == 1):
                  min_wealth = 0
                  # Corrected wealth assignment: ensure randint is used correctly
              else:
                  min_wealth = df[df['Decile'] == (decile-1)]['Wealth'].min()
              max_wealth = df[df['Decile'] == (decile)]['Wealth'].max()

              initial_wealth = np.random.uniform(min_wealth, max_wealth, size=agents_to_add)

          parentsA = np.random.choice(df[df['Decile'] == decile]['ID'], size=agents_to_add, replace=False) #Assumse a pologagramist relationship
          remaining_ids = df[df['Decile'] == decile]['ID'].loc[~df[df['Decile'] == decile]['ID'].isin(parentsA)]
          parentsB = np.random.choice(remaining_ids, size=agents_to_add, replace=False)

          new_entries = pd.DataFrame({
              'ID': new_ids,
              'Wealth': initial_wealth,
              'Initial Wealth (T=0)': initial_wealth,
              'Decile': [decile] * agents_to_add,
              "ParentA": parentsA,
              "ParentB": parentsB ,
              'Status': [3] * agents_to_add,  # Newborn agents start with status 3
              'Age': [18] * agents_to_add,
          })

          new_agents.append(new_entries)
          max_id += agents_to_add  # Update max_id

      elif new_count < count:
          drop_indices = df[df['Decile'] == decile].sample(n=(count - new_count)).index
          df = df.drop(drop_indices)

  # Append new agents to the original DataFrame
  if new_agents:
      new_agents_df = pd.concat(new_agents, ignore_index=True)
      df = pd.concat([df, new_agents_df], ignore_index=True)

  return df

def simulate_trade(df):
    df = df.copy()
    indices = df.index.to_numpy()
    np.random.shuffle(indices)

    for i in range(0, len(indices) - 1, 2):
        idx1 = indices[i]
        idx2 = indices[i + 1]

        # Ensure both agents have status == 0 before trading
        if df.at[idx1, 'Status'] != 0 or df.at[idx2, 'Status'] != 0:
            continue

        decile1 = ( df.at[idx1, 'Decile'])
        decile2 = (df.at[idx2, 'Decile'])

        indicator = 0





        person_A_wealth = df.at[idx1, 'Wealth']
        person_B_wealth = df.at[idx2, 'Wealth']
       # print("index", idx1 , "decile", decile1, "wealth", person_A_wealth)
      #  print("index", idx2 , "decile", decile2, "wealth", person_B_wealth)

        # Compute trade probability based on decile difference
        decile_diff = abs(decile1 - decile2)
        trade_prob = 1 / (decile_diff + 1)
        if trade_prob > 0.25:
          indicator = 1
        #risk_aversion = 0.1
        #random_number = np.random.normal(-1, 1) + risk_aversion
        #person_A_share = random_number
        #person_B_share = 1 - random_number

        # Define value generated from trade

        #TBD: trade_value = np.random.uniform(min(person_A_wealth, person_B_wealth),
                                 #      max(person_A_wealth * 0.5 , person_B_wealth05)) * np.random.uniform(0, 1)
        risk_aversiona = np.random.uniform(0.25,0.75) # For the Future Change factor between some lower value and moveable assit share(share of stocks)
        risk_aversionb = np.random.uniform(0.25,0.75)
        investmentA = np.random.uniform(0,person_A_wealth*risk_aversiona)
        investmentB = np.random.uniform(0,person_B_wealth *risk_aversionb)
        pooled_investment = investmentA + investmentB +1
        mean = 0.1
        std_dev = 0.2
        lower_bound = -1  # in terms of standard deviations
        upper_bound = 1 # define of rate of pooled evaluation

        rate__pooled_investment = np.random.normal(mean,std_dev)
        # Convert bounds to truncnorm's standard normal scale
        a, b = lower_bound, upper_bound

        # Generate one random R value from truncated normal
        #rate__pooled_investment = truncnorm.rvs(a, b, loc=mean, scale=std_dev)

        #print("Rate of return (R):", rate__pooled_investment)
       # print(rate__pooled_investment)
        personA_share = investmentA / pooled_investment
        personB_share = investmentB / pooled_investment

        PersonA_gain = indicator * (1+rate__pooled_investment) * pooled_investment * personA_share # Pooled Investment is getting cancelled out.
        PersonB_gain = indicator * (1+rate__pooled_investment) * pooled_investment * personB_share




        # Alternative approach: mean of random contributions
        #tradeable_wealth = np.mean([np.random.uniform(0, person_A_wealth * 0.5),
        #                            np.random.uniform(0, person_B_wealth * 0.5)])
       # PersonA_gain = trade_prob * person_A_share * tradeable_wealth
        #PersonB_gain = trade_prob * person_B_share * tradeable_wealth

        #PersonA_gain2 = trade_prob * person_A_share * trade_value
        #PersonB_gain2 = trade_prob * person_B_share * trade_value

        df.at[idx1, 'PersonAintermGain']= PersonA_gain
        df.at[idx2, 'PersonBintermGain']= PersonB_gain
        df.at[idx1, 'TradePartner']= idx2
        df.at[idx2, 'TradePartner']= idx1

        #df.at[idx1, 'PersonAtermGain']= PersonA_gain2
        #df.at[idx2, 'PersonBtermGain']= PersonB_gain2

    return df

def Trade_Calculations(df, config):
    df = df.copy()

    rate_of_return = config["rate_of_return"]
    cg_Tax = config["cg_tax"]
    savings_rate = config["savings_rate"]
    unemployment_rate = config["unemployment_rate"]
    wage_band_low = config["wage_band_low"]
    wage_band_high = config["wage_band_high"]

    b = np.percentile(df['PersonAintermGain'].dropna(), 50)
    a = np.percentile(df['PersonAintermGain'].dropna(), 25)
    c = np.percentile(df['PersonAintermGain'].dropna(), 75)

    wealth_tax = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 0.1, 10: 0.2}

    indices = df.index.to_numpy()
    for i in range(0, len(indices) - 1, 2):
        idx1 = indices[i]

        # Ensure TradePartner exists and is valid
        if 'TradePartner' not in df.columns or pd.isna(df.at[idx1, 'TradePartner']):
            continue
        idx2 = int(df.at[idx1, 'TradePartner'])
        if idx2 not in df.index:
            continue

        if df.at[idx1, 'Status'] != 0 or df.at[idx2, 'Status'] != 0:
            continue

        decile1 = int(df.at[idx1, 'Decile'])
        decile2 = int(df.at[idx2, 'Decile'])

        # Employment rate
        employment_ratea = 1 - unemployment_rate[decile1 - 1]
        employment_rateb = 1 - unemployment_rate[decile2 - 1]

        # Wage calculation
        wage_a = np.random.uniform(wage_band_low[decile1 - 1], wage_band_high[decile1 - 1]) * employment_ratea
        wage_b = np.random.uniform(wage_band_low[decile2 - 1], wage_band_high[decile2 - 1]) * employment_rateb

        df.at[idx1, 'Wages'] = wage_a
        df.at[idx2, 'Wages'] = wage_b

        # Income and gain
        person_A_wealth = df.at[idx1, 'Wealth']
        person_B_wealth = df.at[idx2, 'Wealth']
        PersonA_gain = df.at[idx1, 'PersonAintermGain']
        PersonB_gain = df.at[idx2, 'PersonBintermGain']

        Total_Incomea = PersonA_gain + wage_a
        Total_Incomeb = PersonB_gain + wage_b

        df.at[idx1, 'Total_Income'] = Total_Incomea
        df.at[idx2, 'Total_Income'] = Total_Incomeb

        def apply_income_tax_and_savings(gain, decile):
            if gain < a:
                tax_rate = 0.0
            elif a <= gain < b:
                tax_rate = 0.1
            elif b <= gain < c:
                tax_rate = 0.2
            else:
                tax_rate = 0.3

            save_rate = savings_rate[min(decile - 1, len(savings_rate) - 1)]
            income_tax = gain * tax_rate if gain > 0 else 0
            net_income = gain - income_tax
            return income_tax, max(0, net_income * save_rate)

        PersonA_income_tax, PersonA_savings = apply_income_tax_and_savings(Total_Incomea, decile1)
        PersonB_income_tax, PersonB_savings = apply_income_tax_and_savings(Total_Incomeb, decile2)

        df.at[idx1, 'Wealth(T-1)'] = person_A_wealth
        df.at[idx2, 'Wealth(T-1)'] = person_B_wealth

        df.at[idx1, 'Income Tax Collected'] = PersonA_income_tax
        df.at[idx2, 'Income Tax Collected'] = PersonB_income_tax

        df.at[idx1, 'CG Tax Collected'] = person_A_wealth * rate_of_return[decile1 - 1] * cg_Tax
        df.at[idx2, 'CG Tax Collected'] = person_B_wealth * rate_of_return[decile2 - 1] * cg_Tax

        df.at[idx1, 'INCREMENTAL WEALTH FROM GAINS FROM TRADE'] = PersonA_savings
        df.at[idx2, 'INCREMENTAL WEALTH FROM GAINS FROM TRADE'] = PersonB_savings

        # Compute net incremental returns
        PersonANetIncrementalReturns = person_A_wealth + PersonA_savings - df.at[idx1, 'CG Tax Collected']
        PersonBNetIncrementalReturns = person_B_wealth + PersonB_savings - df.at[idx2, 'CG Tax Collected']

        df.at[idx1, 'Net Incremental Wealth From Returns'] = PersonANetIncrementalReturns
        df.at[idx2, 'Net Incremental Wealth From Returns'] = PersonBNetIncrementalReturns

        # Wealth tax
        PersonAWealthTax = person_A_wealth * wealth_tax.get(decile1, 0)
        PersonBWealthTax = person_B_wealth * wealth_tax.get(decile2, 0)

        df.at[idx1, 'Wealth Tax on Wealth(T-1)'] = PersonAWealthTax
        df.at[idx2, 'Wealth Tax on Wealth(T-1)'] = PersonBWealthTax

        # Final wealth update
        df.at[idx1, 'Total Wealth(T)'] = person_A_wealth + PersonANetIncrementalReturns - PersonAWealthTax
        df.at[idx2, 'Total Wealth(T)'] = person_B_wealth + PersonBNetIncrementalReturns - PersonBWealthTax

        df.at[idx1, 'Wealth Change'] = df.at[idx1, 'Total Wealth(T)'] - person_A_wealth
        df.at[idx2, 'Wealth Change'] = df.at[idx2, 'Total Wealth(T)'] - person_B_wealth

    return df

def update_deciles(df):
    df = df.copy()

    # Store old decile before reassignment
    if 'Decile' in df.columns:
        df['Previous Decile'] = df['Decile']
    else:
        df['Previous Decile'] = np.nan

    # Sort and assign new deciles
    df = df.sort_values('Wealth', ascending=False)
    active_mask = (df['Status'] != 1) & df['Wealth'].notna()

    # Compute new decile assignment and bin edges
    deciles, bin_edges = pd.qcut(
        df.loc[active_mask, 'Wealth'],
        q=10,
        labels=False,
        retbins=True,
        duplicates='drop'
    )
    df.loc[active_mask, 'Decile'] = deciles + 1  # Convert to 1-based indexing

    # Construct cutoff structure
    cutoffs = [{"decile": i + 1, "lower": float(bin_edges[i]), "upper": float(bin_edges[i + 1])}
               for i in range(len(bin_edges) - 1)]

    # Transition matrix logic
    transitioned = df.loc[active_mask & df['Previous Decile'].notna()].copy()
    transitioned['Previous Decile'] = transitioned['Previous Decile'].astype(int)
    transitioned['Decile'] = transitioned['Decile'].astype(int)

    transition_counts = transitioned.groupby(['Previous Decile', 'Decile']).size()
    total_per_original = transitioned.groupby('Previous Decile').size()

    transition_df = transition_counts.reset_index(name='Count')
    transition_df['Percent'] = transition_df.apply(
        lambda row: 100 * row['Count'] / total_per_original.loc[row['Previous Decile']],
        axis=1
    )

    pivot_percent = transition_df.pivot(index='Previous Decile', columns='Decile', values='Percent').fillna(0)

    # Convert transition matrix to nested dict (for JSON serializability)
    transition_matrix = pivot_percent.to_dict()

    return df, cutoffs, transition_matrix

def distribute_Inheritance(df, stateCollections):
    df = df.copy()
    indices = df.index.to_numpy()
    inheritance_tax_rate = 0.3
    for i in range(0, len(indices) - 1, 1):
        idx1 = indices[i]
        if df.at[idx1, 'Status'] != 1:
          continue

        deceased_Parent = df.at[idx1, 'ID']
        deceased_Parent_wealth = df.at[idx1, 'Wealth']
        deceased_Parent_Decile = df.at[idx1, 'Decile']
        inheritance_tax = deceased_Parent_wealth * inheritance_tax_rate
        df.at[idx1, 'Inheritance_Tax'] = inheritance_tax
        deceased_Parent_wealth -= inheritance_tax

        # Find children of deceased parent
        children = df[(df['ParentA'] == deceased_Parent) | (df['ParentB'] == deceased_Parent)]

        if not children.empty:
         # print(children)
          amount_of_children = len(children)
          share_of_wealth = deceased_Parent_wealth / amount_of_children
          for index, row in children.iterrows():
            df.at[index, 'Wealth'] += share_of_wealth
           # print("Share of Wealth", share_of_wealth, index," Amount of Children", amount_of_children)
        else:
          stateCollections += deceased_Parent_wealth
          #print("No children found", stateCollections)
    return df, stateCollections
def redistribute_tax_equally(df):
    df = df.copy()  # Avoid SettingWithCopyWarning
#qeqe1
    tax_columns = [
        'CG Tax Collected',
        'Income Tax Collected',
        'Inheritance_Tax',
        'Wealth Tax on Wealth(T-1)'
    ]

    # Ensure all tax columns exist
    for col in tax_columns:
        if col not in df.columns:
            df[col] = 0.0

    # Calculate total tax collected
    total_tax = df[tax_columns].sum().sum()

    # Identify eligible (non-empty) agents — not dead and Wealth is finite
    mask = (df['Status'] != 1) & (df['Wealth'].notna()) & (np.isfinite(df['Wealth']))
    eligible_agents = df[mask]

    num_agents = len(eligible_agents)
    if num_agents == 0:
        return df  # No one to redistribute to

    tax_share = total_tax / num_agents

    # Apply redistribution only to eligible agents
    df.loc[mask, 'Wealth'] += tax_share
    df.loc[mask, 'Tax Redistribution Received'] = tax_share

    return df
def gini_coefficient(x):
    """Compute Gini coefficient of array of values"""
    x = np.double(x.values)
    x = x / x.sum()
    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad / np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g

def compute_gini(array):
    """Compute the Gini coefficient of a numpy array."""
    array = np.sort(array)  # values must be sorted
    n = len(array)
    cum_wealth = np.cumsum(array)
    gini = (n + 1 - 2 * np.sum(cum_wealth) / cum_wealth[-1]) / n
    return gini

def run_simulation(config):
    df_agents = initialize_wealth(config["total_population"], config["wealth_per_decile"])
    results = []
    stateCollections = config.get("state_collections", 0)

    for t in range(config["num_time_steps"]):
        df_agents_copy = df_agents.copy()

        df_agents_copy = update_population(
            df_agents_copy,
            config["birth_rate"],
            config["death_rate"],
            config["net_migration"],
            config["wealth_per_decile"],
            first_time_step=(t == 1)
        )
        df_agents_copy = simulate_trade(df_agents_copy)
        df_agents_copy = Trade_Calculations(df_agents_copy, config)
        df_agents_copy, cutoffs, transition_matrix = update_deciles(df_agents_copy)
        df_agents_copy, stateCollections = distribute_Inheritance(df_agents_copy, stateCollections)

        df_population_changes = df_agents_copy.groupby('Decile').agg(
            Population_Size=('Status', 'size'),
            Number_of_Births=('Status', lambda x: (x == 3).sum()),
            Number_of_Migrations=('Status', lambda x: (x == 2).sum()),
            Number_of_Deaths=('Status', lambda x: (x == 1).sum()),
            Total_Wealth=('Total Wealth(T)', 'sum'),
            Total_Wealth_Change=('Wealth Change', 'sum'),
            Average_Wealth=('Total Wealth(T)', 'mean'),
            Average_Wealth_Change=('Wealth Change', 'mean'),
            Total_Income=('Total_Income', 'sum'),
            Average_Income=('Total_Income', 'mean'),
            Total_CG_Tax=('CG Tax Collected', 'sum'),
            Average_CG_Tax=('CG Tax Collected', 'mean'),
            Total_Income_Tax=('Income Tax Collected', 'sum'),
            Average_Income_Tax=('Income Tax Collected', 'mean'),
            Total_Inheritance_Tax=('Inheritance_Tax', 'sum'),
            Average_Inheritance_Tax=('Inheritance_Tax', 'mean'),
            Total_Savings=('INCREMENTAL WEALTH FROM GAINS FROM TRADE', 'sum'),
            Average_Savings=('INCREMENTAL WEALTH FROM GAINS FROM TRADE', 'mean'),
            Total_Wealth_Tax=('Wealth Tax on Wealth(T-1)', 'sum'),
            Average_Wealth_Tax=('Wealth Tax on Wealth(T-1)', 'mean'),
            Total_Wealth_After_Tax=('Total Wealth(T)', 'sum'),
            Average_Wealth_After_Tax=('Total Wealth(T)', 'mean')
        ).reset_index()

        df_population_changes['Gini_Wealth'] = df_agents_copy.groupby('Decile')['Wealth'].apply(gini_coefficient).values

      #  df_population_changes.to_csv(f"df_population_changes{t}.csv", index=False)

        # At the end of each time step loop in run_simulation:
        # --- 10th Decile ---
        row_10th = df_population_changes[df_population_changes['Decile'] == 10]
        wealth_10th = row_10th['Total_Wealth'].values[
            0] if not row_10th.empty and 'Total_Wealth' in row_10th.columns else 0

        # --- 1st Decile ---
        row_1st = df_population_changes[df_population_changes['Decile'] == 1]
        wealth_1st = row_1st['Total_Wealth'].values[0] if not row_1st.empty and 'Total_Wealth' in row_1st.columns else 0

        # --- Bottom 50%: sum of deciles 1 to 5 ---
        bottom_50_df = df_population_changes[df_population_changes['Decile'].between(1, 5)]
        wealth_bottom_50 = bottom_50_df['Total_Wealth'].sum()

        # --- Total ---
        total_wealth = df_population_changes['Total_Wealth'].sum() or 1  # Prevent divide-by-zero

        # --- Shares ---
        wealth_share_10th = wealth_10th / total_wealth
        wealth_share_1st = wealth_1st / total_wealth
        wealth_share_bottom_50 = wealth_bottom_50 / total_wealth

        #--Wealth-Inequality--

        ratio_90_10 = wealth_10th / wealth_1st if wealth_1st else float('inf')
        ratio_90_50 = wealth_10th / wealth_bottom_50 if wealth_bottom_50 else float('inf')

        #--Gini_Wealth
        gini_wealth = compute_gini(df_population_changes['Total_Wealth'].values)

        try:
            gini_income = compute_gini(df_population_changes['Total_Income'].values)
        except KeyError:
            gini_income = None
        cg_tax_by_decile = df_population_changes.set_index("Decile")["Total_CG_Tax"].to_dict()
        total_wealth_tax = df_population_changes["Total_Wealth_Tax"].sum()
        total_cg_tax = df_population_changes["Total_CG_Tax"].sum()
        total_income_tax = df_population_changes["Total_Income_Tax"].sum()
        total_inheritance_tax = df_population_changes["Total_Inheritance_Tax"].sum()
        total_tax = total_wealth_tax + total_cg_tax + total_income_tax + total_inheritance_tax

        # --- Append to results ---
        results.append({
            "time": t,
            "gini_index": gini_coefficient(df_agents_copy["Wealth"]),
            "total_wealth": df_agents_copy["Wealth"].sum(),
            "population": len(df_agents_copy),
            "state_collections": stateCollections,
            "wealth_by_decile": df_agents_copy.groupby("Decile")["Wealth"].mean().to_dict(),
            "wealth_tax_by_decile": df_population_changes.set_index("Decile")["Total_Wealth_Tax"].to_dict(),
            "total_wealth_tax_collected": df_population_changes["Total_Wealth_Tax"].sum(),
            "tax_per_decile_income": df_population_changes.set_index("Decile")["Total_Income_Tax"].to_dict(),
            "inheritance_tax_by_decile": df_population_changes.set_index("Decile")["Total_Inheritance_Tax"].to_dict(),
            "total_income_tax_collected": df_population_changes['Total_Income_Tax'].sum(),
            "cg_tax_by_decile": cg_tax_by_decile,
            "total_inheritance_tax": df_population_changes['Total_Inheritance_Tax'].sum(),
            "total_cg_tax": df_population_changes['Total_CG_Tax'].sum(),
            "wealth_share_10th_decile": wealth_share_10th,
            "wealth_share_1st_decile": wealth_share_1st,
            "wealth_share_bottom_50": wealth_share_bottom_50,
            "wealth_ratio_90_10": ratio_90_10,
            "wealth_ratio_90_50": ratio_90_50,
            "gini_overall_wealth": gini_wealth,
            "gini_overall_income": gini_income,
            "tax_share_wealth": total_wealth_tax / total_tax if total_tax > 0 else 0,
            "tax_share_cg": total_cg_tax / total_tax if total_tax > 0 else 0,
            "tax_share_income": total_income_tax / total_tax if total_tax > 0 else 0,
            "tax_share_inheritance": total_inheritance_tax / total_tax if total_tax > 0 else 0,
            "decile_cutoffs": {"time": t, "cutoffs": cutoffs},
            "decile_transition_matrix": {"time": t, "matrix": transition_matrix},
        })



        df_agents_copy = df_agents_copy[df_agents_copy['Status'] != 1]
        df_agents_copy.loc[df_agents_copy['Status'].isin([2, 3]), 'Status'] = 0
        df_agents_copy["Age"] += 1
        df_agents_copy.dropna(how='all', inplace=True)

        df_agents = df_agents_copy

    return results