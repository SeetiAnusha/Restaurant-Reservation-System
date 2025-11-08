# Demo Video Script - Restaurant Reservation AI Agent

**Duration**: 3 minutes
**Format**: Screen recording with voiceover

---

## Opening (0:00-0:30)

### Visual
- Show title slide: "GoodFoods AI Reservation Agent"
- Transition to problem statement slide

### Script
> "Meet GoodFoods - a restaurant chain losing $12,000 monthly to no-shows, spending 80 staff-hours weekly on phone reservations, and missing out on revenue from unfilled tables.
>
> Today, I'll show you how an AI-powered conversational agent solves these problems while delivering a delightful customer experience."

---

## Demo 1: Happy Path Booking (0:30-1:00)

### Visual
- Open Streamlit app
- Show clean chat interface
- Type message in real-time

### Script
> "Let's see it in action. I'm Sarah, a busy professional who needs a quick reservation."

**Type**: "I need a table for 4 tomorrow at 7pm, Italian food"

**Agent responds with 3 recommendations**

> "In under 2 seconds, the agent understood my intent, searched 100 restaurants using semantic embeddings, checked real-time availability, and gave me 3 perfect matches."

**Type**: "Bella Notte sounds perfect"

**Agent books and shows confirmation**

> "Booking confirmed with a unique code. Total time: 45 seconds. Compare that to a 5-minute phone call."

---

## Demo 2: Edge Case - Fully Booked (1:00-1:30)

### Visual
- Continue in same chat
- Show alternative handling

### Script
> "But what happens when things go wrong? Let's test an edge case."

**Type**: "Actually, I want to book at the busiest place tonight at 8pm"

**Agent checks availability, finds it's fully booked, suggests alternatives**

> "The agent gracefully handles the fully-booked scenario, offering alternative times at the same restaurant and similar restaurants with availability. No frustration, just solutions."

---

## Demo 3: Multi-Turn Conversation (1:30-2:00)

### Visual
- Start new conversation (click reset button)
- Show multi-turn interaction

### Script
> "The agent excels at natural conversation. Watch how it handles incomplete information."

**Type**: "I want to book a table"

**Agent asks clarifying questions**

**Type**: "For 4 people"

**Agent asks for more details**

**Type**: "Tomorrow at 7pm, something romantic"

**Agent recommends romantic restaurants**

> "It remembers context, asks smart questions, and guides users to successful bookings. This is conversational AI done right."

---

## Code Walkthrough (2:00-2:30)

### Visual
- Split screen: Code editor + architecture diagram
- Highlight key components

### Script
> "Under the hood, here's what makes this powerful:
>
> **Agent Orchestrator** - The brain that coordinates everything
>
> **Tool Execution Layer** - Modular tools for recommendations, availability, and booking
>
> **Hybrid Search** - Combines semantic embeddings with structured filters for intelligent recommendations
>
> **LLM Integration** - Llama 3.3 via Groq for natural language understanding at 10x lower cost than GPT-4
>
> The architecture is modular, scalable, and built for production."

---

## Business Value (2:30-2:50)

### Visual
- Show ROI slide with key metrics
- Highlight vertical expansion opportunities

### Script
> "The business impact is substantial:
>
> - **$237,600 annual benefit** from reduced no-shows, increased bookings, and staff time savings
>
> - **1,220% first-year ROI** on an $18,000 investment
>
> - **95% intent accuracy** in testing across 50 conversation scenarios
>
> But this isn't just for restaurants. The same platform adapts to hotels, salons, healthcare, and co-working spaces - a $9 billion total addressable market."

---

## Closing (2:50-3:00)

### Visual
- Show GitHub repo
- Display contact information
- End with GoodFoods logo

### Script
> "This is more than a reservation system - it's a platform for customer experience transformation.
>
> All code, documentation, and test results are in the GitHub repository.
>
> Thank you for watching!"

---

## Technical Setup for Recording

### Tools Needed
- **Screen Recorder**: Loom, OBS Studio, or QuickTime
- **Microphone**: Clear audio quality
- **Resolution**: 1920x1080 (1080p)
- **Frame Rate**: 30 fps

### Pre-Recording Checklist
- [ ] Clear browser cache and cookies
- [ ] Close unnecessary applications
- [ ] Disable notifications
- [ ] Test microphone levels
- [ ] Prepare demo data (reset database if needed)
- [ ] Have script visible on second monitor
- [ ] Test full flow once before recording

### Recording Tips
1. **Speak clearly and at moderate pace**
2. **Pause between sections** (easier to edit)
3. **Show, don't just tell** - let the demo speak
4. **Keep cursor movements smooth**
5. **Highlight important UI elements** with cursor
6. **Record in one take if possible** (more natural)

### Post-Production
1. **Trim dead space** at beginning/end
2. **Add captions** for accessibility
3. **Include background music** (subtle, non-distracting)
4. **Add transitions** between sections
5. **Export in high quality** (1080p, H.264)

---

## Alternative Demo Flows

### If Time Permits (Extended 5-Minute Version)

#### Additional Demo 4: View Reservations (3:00-3:20)
**Type**: "Show me my reservations"
**Agent lists all bookings**
> "Users can easily view and manage their bookings."

#### Additional Demo 5: Cancellation (3:20-3:40)
**Type**: "Cancel my Bella Notte reservation"
**Agent confirms cancellation**
> "Cancellations are handled instantly with automatic seat restoration."

#### Additional Demo 6: Analytics Dashboard (3:40-4:00)
**Click sidebar analytics button**
**Show booking trends, popular cuisines**
> "Restaurant managers get real-time insights into booking patterns."

#### Additional Demo 7: Evaluation Framework (4:00-4:30)
**Show test_scenarios.py**
**Run evaluation script**
**Display results: 95% pass rate**
> "Automated testing ensures reliability across 50 conversation scenarios."

---

## B-Roll Footage Ideas

If creating a more polished video:

1. **Restaurant scenes** (stock footage)
   - Busy restaurant with diners
   - Host checking reservation book
   - Phone ringing off the hook

2. **Problem visualization**
   - Calendar with crossed-out dates (no-shows)
   - Staff member stressed on phone
   - Empty tables during off-peak hours

3. **Solution visualization**
   - Happy customer using phone
   - Smooth booking flow animation
   - Dashboard with positive metrics

4. **Code snippets** (animated)
   - Tool execution flow
   - LLM API call
   - Database query

---

## Slide Deck (Optional)

If creating slides to accompany demo:

### Slide 1: Title
- GoodFoods AI Reservation Agent
- Subtitle: Transforming Restaurant Operations with Conversational AI

### Slide 2: The Problem
- $362K annual cost from inefficiencies
- 80 staff-hours/week on phone bookings
- 15% no-show rate
- Zero customer insights

### Slide 3: The Solution
- AI-powered conversational agent
- Natural language understanding
- Real-time availability management
- Intelligent recommendations

### Slide 4: Architecture
- High-level system diagram
- Key components highlighted
- Technology stack

### Slide 5: ROI
- $237,600 annual benefit
- 1,220% first-year ROI
- 95% intent accuracy
- <2s response time

### Slide 6: Vertical Expansion
- Hotels: $2.1B TAM
- Salons: $890M TAM
- Healthcare: $4.5B TAM
- Co-working: $650M TAM

### Slide 7: Competitive Advantages
- Hybrid intelligence architecture
- Predictive no-show prevention
- White-label platform

### Slide 8: Call to Action
- GitHub repository link
- Contact information
- Thank you

---

## Voiceover Script (Full Text)

```
[0:00-0:10]
Meet GoodFoods - a restaurant chain losing $12,000 monthly to no-shows, 
spending 80 staff-hours weekly on phone reservations, and missing out on 
revenue from unfilled tables.

[0:10-0:20]
Today, I'll show you how an AI-powered conversational agent solves these 
problems while delivering a delightful customer experience.

[0:20-0:30]
Let's see it in action. I'm Sarah, a busy professional who needs a quick 
reservation.

[0:30-0:45]
In under 2 seconds, the agent understood my intent, searched 100 restaurants 
using semantic embeddings, checked real-time availability, and gave me 3 
perfect matches.

[0:45-1:00]
Booking confirmed with a unique code. Total time: 45 seconds. Compare that 
to a 5-minute phone call.

[1:00-1:10]
But what happens when things go wrong? Let's test an edge case.

[1:10-1:30]
The agent gracefully handles the fully-booked scenario, offering alternative 
times at the same restaurant and similar restaurants with availability. No 
frustration, just solutions.

[1:30-1:40]
The agent excels at natural conversation. Watch how it handles incomplete 
information.

[1:40-2:00]
It remembers context, asks smart questions, and guides users to successful 
bookings. This is conversational AI done right.

[2:00-2:10]
Under the hood, here's what makes this powerful:

[2:10-2:30]
Agent Orchestrator - The brain that coordinates everything. Tool Execution 
Layer - Modular tools for recommendations, availability, and booking. Hybrid 
Search - Combines semantic embeddings with structured filters. LLM Integration 
- Llama 3.3 via Groq for natural language understanding at 10x lower cost 
than GPT-4. The architecture is modular, scalable, and built for production.

[2:30-2:40]
The business impact is substantial: $237,600 annual benefit from reduced 
no-shows, increased bookings, and staff time savings.

[2:40-2:50]
1,220% first-year ROI on an $18,000 investment. 95% intent accuracy in 
testing across 50 conversation scenarios.

[2:50-3:00]
But this isn't just for restaurants. The same platform adapts to hotels, 
salons, healthcare, and co-working spaces - a $9 billion total addressable 
market. This is more than a reservation system - it's a platform for customer 
experience transformation. All code, documentation, and test results are in 
the GitHub repository. Thank you for watching!
```

---

## Recording Checklist

### Before Recording
- [ ] Database populated with 100 restaurants
- [ ] .env file configured with valid API key
- [ ] Streamlit app running smoothly
- [ ] Browser window sized appropriately
- [ ] Microphone tested
- [ ] Script reviewed and practiced
- [ ] Demo flow tested end-to-end

### During Recording
- [ ] Speak clearly and confidently
- [ ] Follow script timing
- [ ] Show cursor movements deliberately
- [ ] Pause between major sections
- [ ] Demonstrate all key features

### After Recording
- [ ] Review for audio/video quality
- [ ] Check for any errors or glitches
- [ ] Add captions if needed
- [ ] Export in correct format
- [ ] Upload to appropriate platform

---

## Video Hosting Options

1. **YouTube** (Unlisted)
   - Best for sharing with evaluators
   - Easy embedding in README
   - Good analytics

2. **Loom**
   - Quick and easy
   - Automatic transcription
   - Direct link sharing

3. **Vimeo**
   - Professional appearance
   - Better privacy controls
   - Higher quality playback

4. **Google Drive**
   - Simple sharing
   - No account required to view
   - Good for large files

**Recommendation**: YouTube (Unlisted) for best compatibility and embedding in GitHub README.

---

## Final Tips

1. **Energy**: Be enthusiastic but not over-the-top
2. **Pacing**: Speak at 150-160 words per minute
3. **Clarity**: Enunciate technical terms clearly
4. **Confidence**: You built this - show pride in your work
5. **Authenticity**: Let your personality shine through

Good luck with your demo! 🎬
