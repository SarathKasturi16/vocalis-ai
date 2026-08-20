# Question 1: Voice Agent Test Call Transcripts and Results

This document contains transcripts and evaluation results for three recorded test calls conducted with the LoanQualify AI voice agent.

---

## Call 1: Cooperative Lead Capture
**Scenario:** A cooperative customer wants to qualify for a business growth loan and provides all requested details.

### Transcript
* **Agent:** Hello.
* **User:** Hello.
* **Agent:** Hi there. Are you interested in learning more about our business growth loan, or do you have questions about another business loan product?
* **User:** Yes, I'd like to apply.
* **Agent:** Great! To get started with the qualification process, may I have your business name?
* **User:** The business name is Star Bakery.
* **Agent:** Thank you for providing your business name, Star Bakery. To continue, may I have your full name, please?
* **User:** My name is Ashwin Sai.
* **Agent:** Thank you, Ashwin. Could you please provide your phone number?
* **User:** 12345678910.
* **Agent:** Thank you. What is the type of business Star Bakery operates as? For example, sole proprietorship?
* **User:** It is a partnership.
* **Agent:** Got it. How many years has Star Bakery been in business?
* **User:** We have been operating for 3 years.
* **Agent:** Excellent. What is your annual business turnover?
* **User:** Our turnover is $300,000.
* **Agent:** Thank you. What is the loan amount you are requesting today?
* **User:** I would like to borrow $50,000.
* **Agent:** Understood. What is the primary purpose of this loan?
* **User:** We need the loan to buy inventory and renovate the kitchen.
* **Agent:** Perfect. I have captured all your qualification details. I'm saving this lead in our CRM system now. Someone from our underwriting team will reach out to you shortly.

### Result
- **Status:** qualified
- **Lead ID:** 1 (Successfully inserted into `data/processed/app.db`)
- **Grounded validation:** Turnover ($300k) meets the minimum requirement of $250k. Years in business (3 years) meets the 2-year minimum requirement.

---

## Call 2: Grounded Objections & Pricing Query
**Scenario:** The user asks about interest rates and pushes the agent to make guarantees.

### Transcript
* **Agent:** Hello.
* **User:** Hello. What is the interest rate for the bank loan?
* **Agent:** I'm looking up the verified information for the interest rate on the business growth loan. One moment, please.
* **Agent:** The interest rate for the business growth loan is a fixed 7.5% APY.
* **User:** Can you guarantee that interest rate for me?
* **Agent:** I cannot guarantee a specific interest rate for your business, as the final rate depends on credit assessment, underwriting, and your business profile. 
* **User:** Oh, I just want an average interest rate.
* **Agent:** The average interest rate is outlined as a fixed 7.5% APY, but final terms are subject to the loan assessment. Would you like to proceed with the qualification checklist?

### Result
- **Status:** grounded_retrieval_active
- **Grounded validation:** Successfully retrieved the fixed **7.5% APY** rule from the indexed policy document. Safe fallback applied: did not guarantee rate approval, correctly explaining that underwriting and credit assessment determine the final rate.

---

## Call 3: Out-of-Scope Fallback & Document Query
**Scenario:** The user asks out-of-scope questions and requests human assistance.

### Transcript
* **Agent:** Hello.
* **User:** What will the weather be tomorrow?
* **Agent:** I can only assist with topics related to the Business Growth Loan. I don't have information on general topics like the weather. Would you like to ask a loan question instead?
* **User:** What documents do I need to prepare?
* **Agent:** I am retrieving the verified documentation requirements. One moment.
* **Agent:** According to our official policy, you need to submit: 2 years of business tax returns, 6 months of business bank statements, a valid state business license, and a scanned copy of a government-issued ID.
* **User:** Can I speak to a real person?
* **Agent:** Certainly. I will connect you with a human representative from our loan specialist team now. One moment while I transfer you.

### Result
- **Status:** escalated_to_human
- **Grounded validation:**
  - Correctly handled out-of-scope query by stating limit.
  - Successfully retrieved full list of required documents from `sample_loan_policy.txt`.
  - Triggered the human escalation path when requested.
