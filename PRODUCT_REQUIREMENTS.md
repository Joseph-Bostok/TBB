# TBB Therapy Bot - Product Requirements Document (PRD)

## Product Overview

**Product Name:** TBB Therapy Bot
**Version:** 1.0
**Status:** MVP Complete, Ready for Scale
**Last Updated:** January 20, 2025

---

## Vision & Mission

### Vision
Make mental health support accessible to anyone with a phone, anywhere, anytime.

### Mission
Provide AI-powered therapy support via SMS that:
- Is available 24/7 without appointments
- Requires no app installation
- Remembers conversations and important dates
- Detects crisis situations and provides immediate help
- Delivers evidence-based therapeutic approaches

---

## Problem Statement

### Current State
- **40 million Americans** suffer from anxiety disorders
- **Average wait time** for therapist: 2-4 weeks
- **Cost barrier:** $100-200 per therapy session
- **Stigma:** Many avoid seeking help
- **Accessibility:** Limited availability in rural areas

### User Pain Points
1. "I need help now, not in 3 weeks"
2. "I can't afford $150/session"
3. "I don't want to download another app"
4. "I'm embarrassed to ask for help"
5. "My therapist doesn't remember what I told them last time"

---

## Target Users

### Primary Personas

#### 1. College Student Sarah
- **Age:** 19
- **Issue:** Anxiety about exams, social situations
- **Behavior:** Texts friends frequently, doesn't want parents to know
- **Needs:** Quick coping strategies, exam prep support
- **Quote:** "I just need someone to talk to at 2 AM when I'm stressed"

#### 2. Working Professional Marcus
- **Age:** 32
- **Issue:** Work stress, imposter syndrome
- **Behavior:** Always on phone, no time for appointments
- **Needs:** CBT techniques, motivation, work-life balance
- **Quote:** "I can't take time off for therapy appointments"

#### 3. Rural Parent Jennifer
- **Age:** 45
- **Issue:** Depression, parenting stress
- **Behavior:** Limited access to mental health services
- **Needs:** Emotional support, parenting strategies
- **Quote:** "The nearest therapist is 90 miles away"

### Secondary Personas
- Veterans with PTSD
- LGBTQ+ individuals seeking safe support
- Low-income individuals without insurance
- People in countries with limited mental health resources

---

## User Stories

### Core Functionality

#### As a user, I want to...

**Messaging:**
- [ ] Text a phone number to start a conversation
- [ ] Receive helpful responses within seconds
- [ ] Have the bot remember our previous conversations
- [ ] Get responses that match my communication style

**Crisis Support:**
- [ ] Receive immediate help if I express suicidal thoughts
- [ ] Get emergency resources when I need them
- [ ] Feel safe sharing my darkest thoughts
- [ ] Know someone is watching out for me

**Therapy Approaches:**
- [ ] Get CBT techniques for negative thinking
- [ ] Learn mindfulness exercises for anxiety
- [ ] Receive motivation when I'm feeling down
- [ ] Have the bot know which approach works best for me

**Proactive Support:**
- [ ] Tell the bot about my important exam next week
- [ ] Get a check-in message before the exam
- [ ] Receive follow-up after to see how it went
- [ ] Feel like someone actually cares

**Privacy:**
- [ ] Know my conversations are confidential
- [ ] Not have my data sold to advertisers
- [ ] Control who can see my information
- [ ] Delete my data if I want

---

## Features & Requirements

### MVP Features (✅ Complete)

#### 1. SMS Messaging
**Status:** ✅ Complete
**Description:** Users can text the bot and receive responses
**Technical:** Twilio webhook integration, FastAPI endpoint
**User Value:** No app download, works on any phone

#### 2. Conversation Memory
**Status:** ✅ Complete
**Description:** Bot remembers past conversations
**Technical:** SQLite database, message history retrieval
**User Value:** No need to repeat yourself

#### 3. Crisis Detection
**Status:** ✅ Complete
**Description:** Identifies concerning messages and provides immediate help
**Technical:** Keyword matching, severity scoring, safety incident logging
**User Value:** Potentially life-saving intervention

#### 4. Semantic Routing (Mixture of Experts)
**Status:** ✅ Complete
**Description:** Routes to CBT, Mindfulness, or Motivation expert
**Technical:** Sentence embeddings, cosine similarity
**User Value:** Specialized, effective responses

#### 5. Event Tracking
**Status:** ✅ Complete
**Description:** Remembers important dates and events
**Technical:** AI extraction, database storage
**User Value:** Feels personal and caring

#### 6. Proactive Outreach
**Status:** ✅ Complete
**Description:** Sends check-in messages at appropriate times
**Technical:** APScheduler, scheduled message queue
**User Value:** Ongoing support, not just reactive

#### 7. Personalization
**Status:** ✅ Complete
**Description:** Adapts to user's communication style
**Technical:** Style analysis, JSON profile storage
**User Value:** Feels natural, not robotic

---

### Phase 2 Features (Planned)

#### 8. Voice Calls
**Priority:** High
**Timeline:** 3 months
**Description:** Call the bot for voice conversations
**Technical:** Twilio Voice, speech-to-text, text-to-speech
**User Value:** More natural for some users, accessibility

#### 9. Multi-Language Support
**Priority:** High
**Timeline:** 3 months
**Languages:** Spanish, Mandarin, French, Arabic
**Technical:** Multi-lingual LLM, language detection
**User Value:** Accessible to non-English speakers

#### 10. Therapist Dashboard
**Priority:** High
**Timeline:** 4 months
**Description:** Human oversight and moderation
**Features:**
- View flagged conversations
- Intervene when necessary
- See analytics and trends
- Generate reports
**User Value:** Human safety net, quality assurance

#### 11. User Feedback System
**Priority:** Medium
**Timeline:** 2 months
**Description:** Rate responses, provide feedback
**Technical:** SMS prompts, feedback database
**User Value:** Improve service, feel heard

#### 12. Group Sessions
**Priority:** Medium
**Timeline:** 6 months
**Description:** Multi-user therapy sessions
**Technical:** Group chat rooms, moderated discussions
**User Value:** Peer support, community

#### 13. Progress Tracking
**Priority:** Medium
**Timeline:** 3 months
**Description:** Track mood, anxiety levels over time
**Features:**
- Daily mood check-ins
- Visualization of trends
- Goal tracking
**User Value:** See improvement, stay motivated

---

### Phase 3 Features (Future)

#### 14. Video Sessions
**Timeline:** 12 months
**Description:** Hybrid AI + human therapist video calls

#### 15. EHR Integration
**Timeline:** 12 months
**Description:** Sync with electronic health records

#### 16. Insurance Billing
**Timeline:** 18 months
**Description:** Submit claims to insurance providers

#### 17. Prescription Coordination
**Timeline:** 18 months
**Description:** Coordinate with psychiatrists for medications

---

## User Flows

### Flow 1: First-Time User

```
1. User sees ad/referral for TBB Bot
   ↓
2. User texts "Hello" to +18553592165
   ↓
3. Bot responds:
   "Hi! I'm your TBB therapy bot. I'm here to support you 24/7.
   Everything we discuss is confidential. I can help with:
   • Anxiety and stress
   • Motivation and goals
   • Mindfulness techniques

   What brings you here today?"
   ↓
4. User: "I've been really anxious about my exams"
   ↓
5. Bot detects anxiety topic → Routes to CBT expert
   ↓
6. Bot: "I understand exam anxiety can be overwhelming. Let's work through this together..."
   ↓
7. Conversation continues...
   ↓
8. Bot extracts important event: "exam next Friday"
   ↓
9. Bot: "I'll check in with you before your exam. Good luck preparing!"
   ↓
10. Bot schedules follow-up message for Thursday
```

### Flow 2: Crisis Intervention

```
1. User: "I don't want to be here anymore"
   ↓
2. Crisis detection triggered → Suicide keywords detected
   ↓
3. Bot responds immediately:
   "I'm really concerned about you. Please know that you matter, and help is available.

   🆘 If you're in immediate danger:
   • Call 988 (Suicide & Crisis Lifeline)
   • Text 'HELLO' to 741741 (Crisis Text Line)
   • Call 911

   I'm here to listen if you want to talk."
   ↓
4. Safety incident logged to database
   ↓
5. User flagged for follow-up
   ↓
6. Alert sent to human moderator (if configured)
   ↓
7. Bot continues compassionate conversation
```

### Flow 3: Proactive Check-In

```
1. APScheduler runs at 10:00 AM
   ↓
2. Finds scheduled message: "Check in before Sarah's exam"
   ↓
3. Bot sends SMS:
   "Hey Sarah! Your big exam is tomorrow. How are you feeling?
   Remember the breathing techniques we practiced? 🧘‍♀️"
   ↓
4. Sarah: "Still nervous but more prepared"
   ↓
5. Bot: "That's great progress! Nerves are normal. You've got this! 💪"
   ↓
6. Bot schedules post-exam follow-up for Saturday
```

---

## Success Metrics

### Product Metrics

#### Acquisition
- **Sign-up rate:** % of people who text after seeing ad
- **Activation rate:** % who send 2+ messages
- **Target:** 40% of visitors send first message, 70% of those continue

#### Engagement
- **DAU/MAU ratio:** Daily active users / Monthly active users
- **Target:** 30% (users interact ~10 days/month)
- **Messages per user:** Average messages sent per user per week
- **Target:** 10 messages/user/week
- **Session length:** Average messages per conversation
- **Target:** 5-7 messages per session

#### Retention
- **7-day retention:** % of users active after 7 days
- **Target:** 60%
- **30-day retention:** % of users active after 30 days
- **Target:** 40%
- **Churn rate:** % of users who stop using per month
- **Target:** < 20%

#### Satisfaction
- **NPS (Net Promoter Score):** Would you recommend?
- **Target:** > 50
- **Satisfaction score:** Rate your experience 1-5
- **Target:** 4.2+
- **Crisis intervention success:** Users report feeling better
- **Target:** 80%

### Clinical Outcomes

#### Self-Reported Improvement
- **Anxiety reduction:** % reporting decreased anxiety
- **Target:** 60% after 30 days
- **Depression symptoms:** PHQ-9 score improvement
- **Target:** 3-point reduction after 60 days
- **Coping skills:** Reported increase in coping strategies
- **Target:** 70% report new strategies

#### Behavioral Outcomes
- **Crisis escalations:** Reduction in emergency situations
- **Target:** 50% reduction over 30 days
- **Therapy adherence:** Follow-through on recommendations
- **Target:** 60% practice suggested techniques
- **Real-world application:** Using skills in daily life
- **Target:** 70% report using techniques IRL

---

## Technical Requirements

### Performance
- **Response time:** < 2 seconds for 95% of messages
- **Uptime:** 99.9% availability
- **Concurrency:** Handle 1,000 concurrent users
- **Scalability:** Support 100,000 users without major refactor

### Security
- **Data encryption:** TLS 1.3 for all communications
- **Authentication:** Phone number verification
- **Authorization:** Role-based access control
- **HIPAA compliance:** Business Associate Agreement, audit logs

### Reliability
- **Backup:** Daily automated backups
- **Recovery:** 4-hour RTO (Recovery Time Objective)
- **Monitoring:** Real-time alerting on errors
- **Failover:** Automatic failover to backup systems

### Compatibility
- **SMS:** All carriers in US
- **International:** Support for +50 countries
- **Character encoding:** UTF-8, emoji support
- **Message length:** Handle 160-1600 characters

---

## Dependencies

### External Services
- **Twilio:** SMS gateway (critical)
- **Claude AI:** LLM responses (critical)
- **Firebase:** Phone authentication (optional)
- **Hosting:** AWS/GCP/Heroku (critical)

### Risk Mitigation
- **Twilio alternative:** Vonage as backup
- **LLM alternative:** GPT-4 as backup
- **Multi-region:** Deploy to 2+ regions
- **Vendor lock-in:** Abstract external services

---

## Go-to-Market Strategy

### Target Market
- **Primary:** US market, English-speaking
- **Secondary:** Canada, UK, Australia
- **Tertiary:** Global, multi-language

### Pricing Strategy

#### B2C (Direct to Consumer)
- **Free tier:** 50 messages/month
- **Premium:** $9.99/month unlimited
- **Annual:** $99/year (save 17%)

#### B2B (Healthcare Providers)
- **Small practice:** $500/month (100 patients)
- **Hospital:** $5,000/month (1,000 patients)
- **Enterprise:** Custom pricing

#### B2B2C (Insurance)
- **Per member:** $2-5/member/month
- **Covered benefit:** User pays $0

### Marketing Channels

#### Digital
- **Google Ads:** Target mental health keywords
- **Social media:** Instagram, TikTok mental health content
- **SEO:** Blog about anxiety, depression, coping strategies
- **Partnerships:** Mental health influencers

#### Offline
- **College campuses:** Posters, student health centers
- **Doctor's offices:** Referral cards
- **Support groups:** AA, NAMI, etc.
- **Pharmacies:** Display at checkout

### Launch Plan

#### Beta (Months 1-2)
- 50 hand-picked users
- Active feedback collection
- Daily iteration

#### Limited Launch (Months 3-4)
- 500 users (waitlist)
- Onboarding flow optimization
- Support team trained

#### Public Launch (Month 5)
- Remove waitlist
- PR campaign
- Influencer partnerships

---

## Competitive Analysis

### Direct Competitors

#### Woebot
- **Strengths:** Established, clinical validation, app-based
- **Weaknesses:** App required, less conversational
- **Our advantage:** SMS-first, proactive outreach

#### Replika
- **Strengths:** Highly personalized, emotional connection
- **Weaknesses:** Not therapy-focused, no crisis detection
- **Our advantage:** Evidence-based therapy, safety features

#### Talkspace
- **Strengths:** Real human therapists, insurance covered
- **Weaknesses:** Expensive ($69-99/week), not 24/7 instant
- **Our advantage:** Instant response, lower cost

### Indirect Competitors
- BetterHelp (online therapy)
- Headspace (meditation app)
- Crisis Text Line (crisis-only)

### Competitive Advantages
1. **SMS-first:** No app barrier
2. **Proactive:** Remembers and checks in
3. **Hybrid:** AI speed + human safety
4. **Specialized:** Multiple expert approaches
5. **Affordable:** 10x cheaper than traditional therapy

---

## Open Questions

### Product
- [ ] Should we support MMS (images)?
- [ ] What's the right balance of proactive vs. reactive?
- [ ] How do we handle users who ghost mid-crisis?
- [ ] Should we allow users to switch experts mid-conversation?

### Business
- [ ] What's our relationship with licensed therapists?
- [ ] How do we handle international regulations?
- [ ] Can we get FDA approval as a medical device?
- [ ] What's our liability insurance coverage?

### Technical
- [ ] How do we prevent LLM hallucinations?
- [ ] What's our disaster recovery plan?
- [ ] How do we handle GDPR right-to-be-forgotten?
- [ ] Should we build our own LLM eventually?

---

## Appendix

### Glossary
- **CBT:** Cognitive Behavioral Therapy
- **LLM:** Large Language Model
- **PHQ-9:** Patient Health Questionnaire (depression)
- **GAD-7:** Generalized Anxiety Disorder scale
- **EHR:** Electronic Health Record
- **HIPAA:** Health Insurance Portability and Accountability Act

### References
- NAMI Statistics: https://www.nami.org/mhstats
- Therapy Wait Times: APA Survey 2024
- SMS Usage: Pew Research 2024
- Mental Health Apps: Deloitte Digital Health Report

---

**Document Version:** 1.0
**Owner:** Product Team
**Last Updated:** January 20, 2025
**Status:** Living Document - Update as needed
