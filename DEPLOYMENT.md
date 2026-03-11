# Deployment Guide for Render

This guide will help you deploy the Predictive Maintenance System to Render.

## Prerequisites

- A [Render](https://render.com) account (free tier available)
- Your code pushed to GitHub repository: `https://github.com/Sreemsun/Predictive-Maintenance-System`

## Deployment Steps

### Option 1: Deploy Using render.yaml (Recommended)

1. **Sign in to Render**
   - Go to [https://render.com](https://render.com)
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Blueprint"
   - Connect your GitHub repository: `Sreemsun/Predictive-Maintenance-System`
   - Render will automatically detect the `render.yaml` file

3. **Confirm Settings**
   - Service Name: `predictive-maintenance-system`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn app:app`

4. **Deploy**
   - Click "Apply" to start the deployment
   - Wait for the build to complete (5-10 minutes)

### Option 2: Manual Configuration

1. **Create New Web Service**
   - In Render Dashboard, click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: predictive-maintenance-system
   Region: Oregon (or your preferred region)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && gunicorn app:app
   ```

3. **Set Environment Variables**
   - `PYTHON_VERSION`: `3.11.0`
   - `FLASK_ENV`: `production`
   - `PORT`: (Auto-assigned by Render)

4. **Create Disk Storage (Optional)**
   - Go to "Disks" tab
   - Add disk: `/opt/render/project/src` (1 GB)
   - This persists the SQLite database between deployments

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## Post-Deployment

### Access Your Application

Once deployed, your application will be available at:
```
https://predictive-maintenance-system.onrender.com
```

### Default Login Credentials

```
Admin Account:
Username: admin
Password: admin123

Operator Account:
Username: operator
Password: operator123
```

### Important Notes

1. **Free Tier Limitations**
   - Free tier services spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading to paid tier for production use

2. **Database Persistence**
   - SQLite database is stored on disk
   - Add persistent disk storage to maintain data between deployments
   - For production, consider migrating to PostgreSQL

3. **Static Files**
   - All static files are served correctly from the Flask app
   - No additional CDN configuration needed

## Troubleshooting

### Build Fails

**Issue**: Dependencies fail to install
```bash
# Solution: Check Python version compatibility
# Update render.yaml to specify Python 3.11
```

**Issue**: `joblib` or `gunicorn` not found
```bash
# Solution: Ensure requirements.txt includes:
joblib==1.3.2
gunicorn==21.2.0
```

### Application Won't Start

**Issue**: Module import errors
```bash
# Solution: Check that start command includes 'cd backend'
Start Command: cd backend && gunicorn app:app
```

**Issue**: Port binding error
```bash
# Solution: Ensure app.py reads PORT from environment
port = int(os.environ.get('PORT', 5000))
```

### Database Issues

**Issue**: Database resets on each deployment
```bash
# Solution: Add persistent disk in Render dashboard
# Mount path: /opt/render/project/src
# Size: 1 GB (free tier)
```

**Issue**: Permission errors writing to database
```bash
# Solution: Ensure disk is mounted at correct path
# Check database path in database.py points to writable directory
```

## Monitoring & Logs

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. View real-time application logs

### Monitoring
- Render provides basic metrics (CPU, Memory, Bandwidth)
- Access via "Metrics" tab in service dashboard

## Updating Your Application

### Automatic Deployments
- Push changes to `main` branch
- Render automatically redeploys
- Zero-downtime deployment

### Manual Deployment
1. Go to Render Dashboard
2. Select your service  
3. Click "Manual Deploy"
4. Select branch and deploy

## Custom Domain (Optional)

1. Go to "Settings" tab
2. Scroll to "Custom Domain"
3. Add your domain
4. Update DNS records as instructed
5. SSL certificate auto-provisioned

## Performance Optimization

### For Production Use

1. **Upgrade to Paid Plan**
   - Eliminates spin-down
   - Better performance
   - More resources

2. **Use PostgreSQL**
   - Create PostgreSQL database in Render
   - Update connection string
   - Better for concurrent users

3. **Add Redis**
   - For session management
   - Caching predictions
   - Real-time data

4. **Enable CDN**
   - Faster static file delivery
   - Reduced server load

## Security Recommendations

1. **Change Default Passwords**
   - Update default admin credentials
   - Use environment variables for secrets

2. **Add Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://...
   ```

3. **Enable HTTPS**
   - Automatic with Render
   - Force HTTPS in production

## Cost Estimate

- **Free Tier**: $0/month (with limitations)
- **Starter Plan**: $7/month (750 hours)
- **Standard Plan**: $25/month (always on)

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: https://github.com/Sreemsun/Predictive-Maintenance-System/issues

## Rollback

If deployment fails:
1. Go to "Events" tab
2. Find previous successful deployment
3. Click "Rollback to this version"

---

**Deployment Status**: ✅ Ready for Render deployment
**Last Updated**: March 11, 2026
