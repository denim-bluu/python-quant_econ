# Macroeconomics variable list

## Unsecured

1. UDSC (Unsecured Debt Servicing Cost, replacement for DTI) as the 'Willingness to pay'. 

    $$ 
    UDSC = 100*\frac{\text{Card int rate} * \text{Card bal}+(\text{Loans int rate * (\text{Total Unsec bal} - \text{Card bal})})}{\text{Disposable Income}} 
    $$

    where:

    - Card int rate: IUMCCTL (BOE)
    - Card bal: LPMVZRE (BOE)
    - Loans int rate: IUMBX67 (BOE)
    - Total Unsec bal: LPMBI2P (BOE)
    - Disposable income: RPHQ (ONS)


## Commercial

1. Corporate Income Gearing 
   : The proxy for the debt service capability of firms in the UK economy. It is defined as the interest paid by UK private non-financial companies as a percentage of profits after text.

   $$
    CIG = \frac{\text{Total Interest}}{(\text{Total resource} - \text{Taxes on income and wealth})}
   $$
    where:

    - Total interest: UKEA/I6PK (ONS)
    - Total resource: UKEA/RPBN (ONS)
    - Taxes on income and wealth: UKEA/RPLA (ONS)


2. UK Corporate Profits 
   : UK corporate nominal profits (nominal GDP minus pre-tax labour income, £m.

    $$
    \text{Corporate Profits} = \text{Nominal GDP} - \text{Pre-tax labour income}
    $$

    - PN2/YBHA (ONS)
    - UKEA/ROYJ (ONS)
    - UKEA/ROYH (ONS)
    - UKEA/ROYK (ONS)


## Others

- CPIH: MM23 / L55O (ONS)
- Total Lending to PNFCs = UKEA/NLBC + UKEA/NKZA (ONS)
- UK CPI: MM23/D7BT (ONS)
- UK unemployment rate: LMS/MGSX (ONS)
- UK household income: UKEA/RPQK
-