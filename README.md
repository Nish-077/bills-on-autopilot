# Bills on Autopilot 📄

An AI-powered bill tracking web app that automatically extracts items from bill photos using Google's Gemini AI. Upload your bills, let AI do the work, and track your expenses with beautiful analytics!

## Features

- 📸 **Smart Photo Processing**: Upload multiple bill images at once
- 🤖 **AI-Powered Extraction**: Uses Google Gemini to extract item details automatically
- 💾 **Expense Management**: Add, edit, delete, and search through your expenses
- 📊 **Beautiful Analytics**: View spending patterns, category breakdowns, and trends
- 🌐 **Modern Web Interface**: Clean, responsive Streamlit interface

## Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install all dependencies
- Create a template `.env` file
- Guide you through the setup process

## Supabase Setup (Cloud Database)

1. **Create a free [Supabase](https://supabase.com/) project**
2. In the Table Editor, create a table called `expenditures` with these columns:
   - `id` (integer, primary key, auto-increment)
   - `item` (text)
   - `quantity` (text)
   - `date` (text)
   - `amount` (float8 or numeric)
   - `category` (text)
   - `person` (text)
   - `created_at` (timestamp, default: now())
3. Go to the API settings and copy your **Project URL** and **anon public key**
4. Enable Row Level Security (RLS) and add a policy to allow read/write for anon users:
   - Example policy: `CREATE POLICY "Allow all" ON expenditures FOR ALL USING (true);`
5. Add these to your `.env`:
   ```
   SUPABASE_URL=your_project_url_here
   SUPABASE_KEY=your_anon_public_key_here
   ```

### Option 2: Manual Setup

### 1. Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Setup
```bash
pip install -r requirements.txt
```


Your `.env` file should look like:
```
GOOGLE_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_project_url_here
SUPABASE_KEY=your_anon_public_key_here
```

### 3. Run the App
```bash
streamlit run streamlit_app.py
```

## How to Use


1. **Process Bills**: Upload bill images and let AI extract the items
2. **View Expenses**: Browse, search, edit, and delete your expenses (all data is stored in Supabase)
3. **Analytics**: See spending patterns and category breakdowns

## Deployment

See `DEPLOYMENT.md` for step-by-step instructions to deploy on Streamlit Community Cloud for free.

## Tips for Better Results

- Use clear, well-lit photos
- Ensure text is readable
- Place bills on flat surfaces
- Avoid shadows over the text

## Troubleshooting

- **Supabase insert error**: Make sure you created the table and enabled a permissive RLS policy.
- **Delete not working**: Ensure you select the correct item (each entry now shows its unique ID).
- **Data not saving**: Check your `.env` and Supabase project keys.
