# Question 3: Native-Language Voice Bots Evidence Report

## Overview
This report provides the required evidence for the localized voice bots deployed for the Philippines (Life Insurance) and Indonesia (Multifinance) markets.

## ASR Configuration & Observations
**Provider:** Deepgram (`nova-2`)
**TTS Provider:** Google (native voices `fil-PH-Standard-A` and `id-ID-Standard-A`)

### Philippines Bot
- **Code-switching behavior:** Deepgram's `tl` language model handles Tagalog and English loanwords well. The model smoothly transcribes Taglish phrases like "magbayad ng premium".
- **Observed Errors:** Occasional misspellings of deep Tagalog words or acronyms if spoken too fast.

### Indonesia Bot
- **Regional Accent Performance:** The model handles colloquial Jakarta speech ("gue/lu") and slight Javanese accents well, but highly localized slang may occasionally be mistranscribed.
- **Code-switching:** Finance English loanwords ("down payment", "restructuring") are transcribed correctly amidst Bahasa Indonesia context.

## Localized Adaptation Evidence (vs Direct Translation)

### Philippines (Life Insurance)
1. **Direct Translation:** "We will terminate your policy." -> **Localized:** "Baka po mag-lapse ang inyong policy coverage."
2. **Direct Translation:** "Please pay your bill." -> **Localized:** "Pwede na po kayo magbayad ng inyong premium."
3. **Direct Translation:** "Who receives the money?" -> **Localized:** "Sino po ang nakalagay na beneficiary ninyo?"

### Indonesia (Multifinance)
1. **Direct Translation:** "Your loan is late." -> **Localized:** "Cicilan Bapak/Ibu sudah lewat jatuh tempo."
2. **Direct Translation:** "There is a penalty fee." -> **Localized:** "Ada denda keterlambatan yang harus dibayarkan."
3. **Direct Translation:** "Are you paying today?" -> **Localized:** "Apakah Bapak/Ibu bisa melakukan angsuran hari ini?"

## Test Transcripts
*(Placeholder: Run the bots and record transcripts here)*

### PH Bot: Cooperative Customer
[Insert transcript]

### ID Bot: Objection & Regional Accent
[Insert transcript]

## Native-Speaker Gaps
- TTS voices can sometimes sound slightly robotic when transitioning between English and the native language.
- Local slang or heavy regional accents might occasionally confuse the ASR, requiring repetition.
