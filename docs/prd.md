# Product Requirements Document (PRD): Dreamware

**Version:** 1.0  
**Status:** Draft  
**Date:** October 26, 2025  
**Document Owner:** Project Lead

---

## 1. Executive Summary

- **Product Name:** Dreamware
- **Concept:** A visual-first aggregation platform for AI-generated software concepts ("Dream Coding").
- **Core Value Prop:** Dream coding disconnects the idea from the implementation. Dreamware connects them back together.
Dreamware is a "Pinterest for Engineers" – a platform where users can share, discover, and iterate on software ideas (called "**Dreams**").
It addresses the problem of fragmented software concepts by providing a structured way to visualize, describe, and refine app ideas before a single line of code is written.
Users ("Dreamers") browse a feed of Dreams, which include AI-generated UI mockups, PRDs, and tech stack choices.
They can "fork" these Dreams to create their own versions or "implement" them by linking to GitHub repos. It allows creators to share "Dreamware" (Concept Art + System Prompts) and invites the community to turn those dreams into deployed apps using AI tools (Replit, Cursor, v0, Bolt).

**Mission:** To become the "Dribbble for AI Apps" — the primary destination where AI-native ideas are discovered, forked, and built.

---

## 2. Problem Statement

1.  **The Fragmented Workflow:** "Dream coders" generate amazing app ideas and visuals (Google Nano Banana, GPT image) but often lack the persistence to deploy them.
2.  **No Central Gallery:** Twitter/X is ephemeral. Reddit is text-heavy. Product Hunt is for polished, finished businesses. There is no home for "cool experiments" or "half-finished dreams."
3.  **Collaboration Gap:** Developers often have the skills/tools (Cursor, Replit, Claude code) but lack ideas. Dream coders have ideas but get stuck on implementation.

---

## 3. Target Audience (Personas)

### A. The "Dream Coder" (The Dreamer)
- **Profile:** Uses Google Nano Banana/GPT image for visuals and Claude/ChatGPT for text. May not know React/Python deeply.
- **Goal:** Wants to show off a cool app concept and prompt, hoping someone says "this is cool" or helps build it.
- **Pain Point:** *"I made this amazing UI mockup in v0, but I don't know how to connect the database."*

### B. The "Remixer" (The Builder)
- **Profile:** Comfortable with Cursor, Replit, or Bolt.new. Loves experimenting with new tech stacks.
- **Goal:** Needs inspiration. Wants to take a good prompt, tweak it, and deploy a working version to get clout.
- **Pain Point:** Staring at a blank IDE with no inspiration.

---

## 4. Competitive Analysis

| Competitor | Focus | Gap |
| :--- | :--- | :--- |
| **Product Hunt** | Finished Businesses | Too high-stakes. Rejects "toy" apps or raw concepts. |
| **Dribbble/Behance** | Static Design | No code/prompt sharing. Just visuals. |
| **Reddit (r/SideProject)** | Feedback | Text-heavy. Ugly UI. Hard to find "prompts." |
| **v0.dev / Bolt.new** | Creation Tools | These are editors, not galleries for discovery. |

---

## 5. Core Features (MVP)

### 5.1. The "Dream" Submission (Create Post)
- **Concept Images (Required):** Support for one or more high-res uploads (or AI generation via API if budget allows). The "Dream" is visual.
- **The "System Prompt" (The Source Code):** A structured text field for the actual prompt used to generate the app (e.g., "Create a retro-style Kanban board...").
- **Status:** "Concept Only" vs. "Live Demo."
- **Tags:** AI Tools Used (e.g., `#Cursor`, `#ReplitAgent`, `#GoogleNanoBanana`, `#GPTimage`, `#Claude3.5`).

### 5.2. The Feed (Discovery)
- **Pinterest-Style Grid:** Masonry layout. Minimal text. Hover to see title and "Dream Check" score.
- **Filters:**
  - **By Tool:** "Show me apps built with Replit."
  - **By Tag:** Discover by aesthetics or use case (e.g., `#Cyberpunk`, `#SaaS`).
  - **By Status:** "Show me ideas that need a builder."
  - **Sort by Popularity:** Views, Likes, or "Dream Check" score.

### 5.3. Interaction & Collaboration
- **"Dream Check" (Rating):** High-fidelity quantitative feedback (0-100%).
- **Likes & Social Proof:** Quick "Like" (Heart) for feed ranking.
- **Followers:** Follow creators to build a personal "Dreamware" feed.
- **Collections:** Users can organize Dreams into public/private folders (e.g., "AI Side Projects").
- **Comments & Remix Linking:** Users can post comments on a Dream. Comments can include text and links to their own implementations.
- **"Fork This Dream" (Copy Prompt):** One-click button to copy the System Prompt. This creates a "Lineage" link in the database.
- **"Claim Project":** A user can click "I'm building this." This links their profile to the post as a "Collaborator."

### 5.4. Engagement
- **Notifications:** Real-time (or near real-time) alerts when someone Likes, Comments, or Forks your Dream.

---

## 6. Functional Specifications

### 6.1. User Flow - The "Idea" Lifecycle
1.  **User A** generates a UI mockup in Google Nano Banana.
2.  **User A** posts it on Dreamware with the title "Neon To-Do List" and pastes the Claude prompt they tried to use.
3.  **User A** tags it `#Concept` `#NeedsBuilder`.
4.  **User B (Dev)** sees it, clicks "Copy Prompt," pastes it into Cursor, and fixes the bugs.
5.  **User B** deploys to Vercel.
6.  **User B** returns to Dreamware, comments the Vercel link.
7.  **User A** marks the Vercel link as the "Official Implementation."

### 6.2. Data Model (Schema)

*   **User**
    *   `id` (PK)
    *   `username`
    *   `email`
    *   `avatar`
    *   `portfolio_links` (JSON)
    *   `reputation_score` (Integer)
    *   `google_id` (Nullable String)
    *   `github_id` (Nullable String)

*   **Dream**
    *   `id` (PK)
    *   `creator_id` (FK -> User.id)
    *   `prompt_text` (Text) - The initial user prompt.
    *   `prd_text` (Text, Nullable) - Generated PRD content.
    *   `extra_specs` (JSONB) - Tech stack, colors, aesthetic tags.
    *   `status` (Enum: DRAFT, PUBLISHED, ARCHIVED)
    *   `implementations` (Array of Links/Objects) - Links to actual code.
    *   `created_at`, `updated_at`

*   **DreamImage**
    *   `id` (PK)
    *   `dream_id` (FK -> Dream.id)
    *   `image_url` (String)
    *   `order` (Integer) - To replicate carousel behavior.

*   **Tool**
    *   `id` (PK)
    *   `name` (String, Unique)
    *   `icon_url` (Nullable)
    *   `category` (Nullable)

*   **DreamTool** (Join Table)
    *   `dream_id` (FK)
    *   `tool_id` (FK)

*   **Action/Interaction** (Likes/Collections)
    *   `user_id`
    *   `dream_id`
    *   `type` (LIKE, SAVE)

*   **Review**
    *   `id` (PK)
    *   `dream_id` (FK -> Dream.id)
    *   `user_id` (FK -> User.id)
    *   `score` (Integer 1-5)
    *   `comment` (Text)
    *   `created_at`

*   **Comment**
    *   `id` (PK)
    *   `dream_id` (FK -> Dream.id)
    *   `user_id` (FK -> User.id)
    *   `content` (Text)
    *   `parent_id` (Nullable FK -> Comment.id) - For nested replies
    *   `created_at`

- **Users:** `id`, `username`, `email`, `avatar`, `reputation_score`, `auth_fields`
- **Tools:** `id`, `name`
- **Tags:** `id`, `name` (Aesthetic or category tags)
- **DreamImages:** `id`, `dream_id`, `image_url`
- **Dreams (Posts):**
  - `id`, `creator_id`
  - `parent_dream_id` (Link to the original "forked" Dream)
  - `prompt_text`, `prd_text`, `extra_specs`
  - `status` (Concept, WIP, Live)
  - `tools` (Many-to-Many), `tags` (Many-to-Many)
- **Reviews (Dream Checks):** `id`, `dream_id`, `user_id`, `score`, `comment`
- **Comments:** `id`, `dream_id`, `user_id`, `content`
- **Likes:** `id`, `dream_id`, `user_id`
- **Collections:** `id`, `owner_id`, `name`, `dreams` (Many-to-Many)
- **Followers:** `follower_id`, `followed_id`
- **Notifications:** `id`, `user_id`, `type`, `content`, `link`, `is_read`

---

## 7. Technical Stack Recommendations

- **Frontend:** React, shadcn/ui (using a template).
- **Styling:** Tailwind CSS.
- **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic, managed with `uv`.
- **Database:** PostgreSQL.
- **Storage:** S3 (or similar).
- **Auth:** email + password. + google + github.

---

## 8. Success Metrics (KPIs)

- **Fork Rate:** % of posts where the "Copy Prompt" button is clicked. (This proves utility).
- **Build Rate:** % of "Concept" posts that eventually get a "Live Link" added.
- **Time-to-Vibe:** How fast a user goes from landing page to viewing a prompt.

---

## 9. Future Roadmap (Post-MVP)

- **Direct Integration:** "Open in StackBlitz" or "Open in Replit" buttons that pre-fill the prompt.
- **Bounties:** Users can attach $50 (crypto/Stripe) to a "Concept" for whoever builds it first.
- **Weekly Vibe Batches:** Newsletter featuring the "Top 5 Forked Prompts" of the week.