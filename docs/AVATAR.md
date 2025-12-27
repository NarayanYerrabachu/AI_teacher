# Avatar Video Integration Options

This document outlines different options for adding AI avatar videos to the explanation feature in the AI Education System.

## Current Implementation

The system currently generates:
- ✅ **Animated text explanations** with synchronized timing
- ✅ **Audio narration** using OpenAI Text-to-Speech (TTS)
- ✅ **Frontend layout** ready for avatar video (split-screen: video left, text right)

**Missing:** Avatar video generation (requires API key from one of the providers below)

---

## Option 1: HeyGen Integration ⭐ (RECOMMENDED)

**Status:** Code already implemented, waiting for API access

### Overview
HeyGen provides high-quality AI avatar videos with excellent lip-sync. Perfect for educational content.

### Key Features
- 🎭 **100+ realistic avatars** (various ethnicities, ages, styles)
- 🗣️ **Natural lip-sync** from audio or text
- 🌍 **40+ languages supported**
- 🎬 **Quick generation** (~30-60 seconds per video)
- 📱 **HD quality** (720p-4K)

### Pricing
- **Free Trial:** 1-minute credit
- **Creator Plan:** $29/month (3 minutes)
- **Business Plan:** $89/month (15 minutes)
- **Enterprise:** Custom pricing
- **API Access:** Requires Business plan or higher

### Setup Instructions

#### Step 1: Get API Access
1. Visit https://www.heygen.com/contact-sales
2. Request API access (usually requires Business plan)
3. Wait for approval (1-2 business days)
4. Get your API key from https://app.heygen.com/settings

#### Step 2: Choose Avatar
1. Browse avatars at https://app.heygen.com/avatars
2. Select a young lady avatar (recommended: `Monica_public`, `Anna_public_3_20240108`)
3. Copy the avatar ID

#### Step 3: Configure Backend
Add to `.env`:
```bash
ENABLE_HEYGEN_AVATAR=true
HEYGEN_API_KEY=your_api_key_here
HEYGEN_AVATAR_ID=Monica_public
HEYGEN_VOICE_ID=1bd001e7e50f421d891986aad5158bc8  # Optional
```

#### Step 4: Restart Backend
```bash
cd backend
# Stop and restart your FastAPI server
```

### Integration Details
- **Service:** `backend/heygen_service.py` (already implemented)
- **Method:** Audio-to-video (sends OpenAI TTS audio to HeyGen)
- **Output:** Video URL returned in explanation data
- **Frontend:** Automatically displays video in split-screen layout

### Pros
✅ Excellent quality and lip-sync
✅ Many avatar options
✅ Reliable API
✅ Good documentation
✅ Code already implemented in our system

### Cons
❌ Requires paid plan for API access
❌ Higher cost per minute compared to alternatives
❌ Approval process for API access

---

## Option 2: D-ID (Easier API Access)

### Overview
D-ID offers similar avatar video generation with easier API access and lower pricing.

### Key Features
- 🎭 **50+ realistic avatars**
- 🗣️ **Good lip-sync quality**
- 💰 **More affordable pricing**
- 🚀 **Instant API access** (no approval needed)
- 🎁 **$20 free trial credit**

### Pricing
- **Free Trial:** $20 credit (~20 minutes)
- **Lite Plan:** $5.90/month (10 minutes)
- **Pro Plan:** $29/month (50 minutes)
- **Advanced:** $196/month (500 minutes)
- **API Access:** Available on all plans

### Setup Instructions

#### Step 1: Sign Up
1. Visit https://www.d-id.com/
2. Create free account
3. Get instant API access
4. Copy API key from https://studio.d-id.com/account-settings

#### Step 2: Choose Avatar
1. Browse presenters at https://studio.d-id.com/agents
2. Select avatar and copy presenter ID

#### Step 3: Implementation (NOT YET IMPLEMENTED)
We would need to:
1. Create `backend/did_service.py` similar to `heygen_service.py`
2. Update `explanation_service.py` to use D-ID API
3. Configure in `.env`

### API Example
```python
import requests

url = "https://api.d-id.com/talks"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "source_url": "https://path-to-avatar-image.jpg",
    "script": {
        "type": "audio",
        "audio_url": "data:audio/mp3;base64,{audio_base64}"
    }
}
response = requests.post(url, json=payload, headers=headers)
```

### Pros
✅ Instant API access (no approval)
✅ More affordable pricing
✅ $20 free trial
✅ Good for testing/prototyping
✅ Simple API

### Cons
❌ Slightly lower quality than HeyGen
❌ Fewer avatar options
❌ Code not yet implemented

---

## Option 3: Synthesia (Enterprise-Grade)

### Overview
Synthesia is the premium option, used by Fortune 500 companies. Best quality but highest cost.

### Key Features
- 🎭 **140+ professional avatars**
- 🗣️ **Best-in-class lip-sync**
- 🌍 **120+ languages**
- 🎨 **Custom avatar creation available**
- 🏢 **Enterprise features** (SSO, team collaboration)

### Pricing
- **Starter:** $29/month (10 minutes)
- **Creator:** $89/month (30 minutes)
- **Enterprise:** Custom pricing
- **API Access:** Enterprise plan only

### Setup Instructions

#### Step 1: Contact Sales
1. Visit https://www.synthesia.io/
2. Request demo and API access
3. Enterprise pricing negotiation

#### Step 2: Implementation (NOT YET IMPLEMENTED)
Similar to D-ID, would require new service implementation.

### API Example
```python
import requests

url = "https://api.synthesia.io/v2/videos"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "title": "Educational Explanation",
    "visibility": "private",
    "aspectRatio": "16:9",
    "input": [{
        "avatarSettings": {
            "avatarId": "anna_costume1_cameraA"
        },
        "scriptText": "Your explanation text here",
        "voice": "en-US-1"
    }]
}
response = requests.post(url, json=payload, headers=headers)
```

### Pros
✅ Highest quality avatars
✅ Most professional appearance
✅ Best for enterprise/paid customers
✅ Custom avatar creation
✅ Advanced features

### Cons
❌ Most expensive option
❌ Enterprise plan required for API
❌ Complex approval process
❌ Overkill for small projects

---

## Option 4: Local Video (No API Costs)

### Overview
Pre-generate avatar videos locally and upload them to your server.

### Approach
1. Use free tools like:
   - **OBS Studio** + **VTube Studio** (Live2D avatars)
   - **Unreal Engine** + **MetaHuman** (realistic avatars)
   - **Ready Player Me** (customizable 3D avatars)
2. Record videos for common explanations
3. Store videos on server or S3
4. Match videos to explanation topics

### Pros
✅ No API costs
✅ Full control over avatar
✅ One-time creation cost
✅ No usage limits

### Cons
❌ Manual work for each explanation
❌ Not scalable for dynamic content
❌ Storage costs
❌ Time-consuming production

---

## Comparison Table

| Feature | HeyGen | D-ID | Synthesia | Local |
|---------|--------|------|-----------|-------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | $$$ | $$ | $$$$ | $ (one-time) |
| **API Access** | Needs approval | Instant | Enterprise only | N/A |
| **Free Trial** | 1 min | $20 credit | No | Yes |
| **Ease of Setup** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Code Status** | ✅ Implemented | ❌ Not implemented | ❌ Not implemented | ❌ Not implemented |
| **Best For** | Production use | Testing/prototyping | Enterprise | Budget projects |

---

## Recommendation

### For Production (Current Project):
**HeyGen** is the best choice because:
1. ✅ Code already implemented and tested
2. ✅ Best balance of quality and cost
3. ✅ Reliable API and support
4. ✅ Good for educational content
5. ✅ 100+ avatars to choose from

**Action Plan:**
1. Contact HeyGen sales for API access
2. Upgrade to Business plan ($89/month)
3. Add API key to `.env`
4. Start with 15 minutes/month, upgrade if needed

### For Testing/Budget:
**D-ID** is ideal if:
- You want to test avatar features first
- Budget is limited
- Need instant API access

**Action Plan:**
1. Sign up at d-id.com (5 minutes)
2. Use $20 free credit for testing
3. I'll implement D-ID service if you want this option

---

## When to Enable Avatar Feature

### Current Setup (Without Avatar):
- ✅ Animated text explanations
- ✅ Audio narration
- ✅ Works perfectly for educational content
- ✅ Zero additional costs

### With Avatar (Future):
- 👩‍🏫 Young lady avatar speaking
- 📱 Split-screen: avatar video + animated text
- 💰 Additional cost: $29-89/month
- ⏱️ Additional wait time: 30-60 seconds per video

### Consider Adding Avatar When:
1. You have budget for API costs
2. You want more engaging visual presentation
3. Your user base is large enough to justify cost
4. You've tested current system and want to enhance it

---

## Technical Notes

### Current Implementation
- **File:** `backend/heygen_service.py`
- **Integration:** `backend/explanation_service.py`
- **Frontend:** `frontend/src/components/AnimatedExplanation.tsx`
- **Config:** `.env` variable `ENABLE_HEYGEN_AVATAR`

### To Switch Providers:
1. Create new service file (e.g., `did_service.py`)
2. Update `explanation_service.py` to import new service
3. Update `.env` configuration
4. Frontend automatically adapts (no changes needed)

### Video Requirements:
- **Format:** MP4
- **Resolution:** 720p minimum (1280x720)
- **Aspect Ratio:** 9:16 (portrait) or 16:9 (landscape)
- **Duration:** Matches audio length (10-30 seconds typically)

---

## Support & Resources

### HeyGen
- Website: https://www.heygen.com/
- Docs: https://docs.heygen.com/
- Support: support@heygen.com

### D-ID
- Website: https://www.d-id.com/
- Docs: https://docs.d-id.com/
- Support: Via dashboard chat

### Synthesia
- Website: https://www.synthesia.io/
- Docs: https://docs.synthesia.io/
- Support: Via email/phone (enterprise)

---

## Questions?

Contact the development team or refer to:
- Main README: `README.md`
- Environment config: `.env`
- HeyGen service code: `backend/heygen_service.py`
- Explanation service: `backend/explanation_service.py`
