# Deploy to Render - Step by Step Guide

## Prerequisites
- Render account (free at render.com)
- GitHub account
- Your Django project files ready

## Step 1: Prepare Your Code

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Ready for Render deployment"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Verify required files are present:**
   - `render.yaml` (I've created this for you)
   - `requirements.txt` (already includes gunicorn and whitenoise)
   - `.env.example` (I've updated this for you)
   - Updated `settings.py` (I've configured this for Render)

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended)
1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect your `render.yaml` file
6. Click "Create Web Service"

### Option B: Manual Setup
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the following:
   - **Name**: jaljala-school-website
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn school_project.wsgi:application`
   - **Python Version**: 3.11.0

## Step 3: Set Up Database

1. After creating the web service, go to "New +" → "PostgreSQL"
2. Configure:
   - **Name**: school-db
   - **Database Name**: school_db
   - **User**: school_user
   - **Plan**: Free
3. Click "Create Database"

## Step 4: Add Environment Variables

In your web service settings, add these environment variables:

```
DJANGO_SETTINGS_MODULE=school_project.settings
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
DATABASE_URL=(auto-populated from Render database)
```

## Step 5: Run Migrations

1. Once deployed, go to your web service
2. Click "Shell" in the Render dashboard
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

## Step 6: Configure Email (Optional)

If you want email functionality:
1. Set up a Gmail account with App Password
2. Add these environment variables:
   - `EMAIL_HOST_USER=your-email@gmail.com`
   - `EMAIL_HOST_PASSWORD=your-app-password`

## Step 7: Test Your Deployment

1. Wait for the deployment to complete (5-10 minutes)
2. Visit your Render URL (e.g., https://jaljala-school-website.onrender.com)
3. Test all functionality including:
   - Homepage loading
   - Admin panel access
   - Image uploads
   - Form submissions

## Troubleshooting

### Build Fails
- Check the build logs in Render dashboard
- Ensure all dependencies are in requirements.txt
- Verify Python version compatibility

### Database Connection Issues
- Ensure DATABASE_URL is properly set
- Check that the database is in the same region as your web service
- Verify database credentials

### Static Files Not Loading
- Ensure whitenoise is installed
- Check that collectstatic ran successfully
- Verify STATIC_URL and STATIC_ROOT settings

### 502 Bad Gateway
- Check that gunicorn is running
- Verify the start command
- Check application logs

## Custom Domain (Optional)

1. In your web service settings, click "Domains"
2. Add your custom domain (e.g., www.shreejaljala.edu.np)
3. Update DNS records as instructed by Render
4. Update DJANGO_ALLOWED_HOSTS to include your domain

## Monitoring

- Monitor your deployment in the Render dashboard
- Check logs for errors
- Set up alerts for downtime
- Monitor database usage

## Cost

- **Free Tier**: Available for web services and PostgreSQL
- **Paid Plans**: Start at $7/month for better performance
- Database: Free tier includes 90 days of backups

## Support

- Render Documentation: https://render.com/docs
- Django Deployment Guide: https://docs.djangoproject.com/en/stable/howto/deployment/