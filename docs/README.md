# SEOdaily-ENG Documentation

Complete documentation for the Seoul Economic Daily English news platform.

---

## 📚 Quick Navigation

### Development History
- **[Development Phases](phases/README.md)** - Complete project timeline (Phase 1-52)
  - Phase-by-phase development history
  - Architectural decisions and rationale
  - Feature implementations and outcomes

### Architecture & Design
- **[System Architecture](ARCHITECTURE.md)** - Overall system design, component interaction, AWS infrastructure
- **[Project Structure](PROJECT_STRUCTURE.md)** - Codebase organization and directory structure
- **[How It Works](HOW_IT_WORKS.md)** - Data flow, article collection, translation pipeline

### API & Data
- **[API Reference](API.md)** - REST API endpoints, request/response formats
- **[Database Schema](DATABASE.md)** - DynamoDB table structure and indexes
- **[Environment Variables](ENVIRONMENT.md)** - Configuration and secrets management

### Operations
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment procedures, CI/CD
- **[Technical Documentation](TECHNICAL.md)** - Performance metrics, cost analysis, security, monitoring
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Development
- **[AI Development Guidelines](AI_GUIDELINES.md)** - AI-assisted development best practices
- **[Work Logs](work-logs/)** - Daily development activity logs (AI context)

### Additional Resources
- **[Archive](archive/)** - Historical deployment logs and legacy documentation
- **[Guides](guides/)** - Specific operational guides (EC2, frontend deployment)
- **[Google Analytics 4](GA4_SETUP.md)** - GA4 integration guide
- **[Google AdSense](ADSENSE_SETUP.md)** - AdSense configuration

---

## 📖 Document Categories

### By Audience

**For New Developers:**
1. Start with [Quick Start](../README.md#quick-start) in root README
2. Read [How It Works](HOW_IT_WORKS.md)
3. Review [Project Structure](PROJECT_STRUCTURE.md)
4. Check [Development Phases](phases/README.md) for context

**For Operations/DevOps:**
1. [Deployment Guide](DEPLOYMENT.md)
2. [Technical Documentation](TECHNICAL.md)
3. [Troubleshooting](TROUBLESHOOTING.md)
4. [Environment Variables](ENVIRONMENT.md)

**For Architects/Tech Leads:**
1. [System Architecture](ARCHITECTURE.md)
2. [Development Phases](phases/README.md) - see evolution
3. [Database Schema](DATABASE.md)
4. [API Reference](API.md)

**For Product/Business:**
1. [Development Phases](phases/README.md) - feature timeline
2. [Technical Documentation](TECHNICAL.md) - performance, costs
3. [How It Works](HOW_IT_WORKS.md) - system capabilities

### By Topic

**Frontend (Next.js):**
- [Architecture](ARCHITECTURE.md) - SSR architecture
- [Project Structure](PROJECT_STRUCTURE.md) - frontend directory
- [Deployment](DEPLOYMENT.md) - EC2 SSR deployment
- [Frontend README](../frontend/README.md) - detailed frontend docs

**Backend (AWS Lambda):**
- [Architecture](ARCHITECTURE.md) - serverless architecture
- [API Reference](API.md) - Lambda function endpoints
- [Database Schema](DATABASE.md) - DynamoDB tables
- [How It Works](HOW_IT_WORKS.md) - article collection pipeline

**Infrastructure (AWS/Terraform):**
- [Architecture](ARCHITECTURE.md) - AWS infrastructure
- [Deployment](DEPLOYMENT.md) - Terraform IaC
- [Technical Documentation](TECHNICAL.md) - monitoring, costs
- [Infrastructure README](../infrastructure/README.md) - Terraform modules

**AI/Translation:**
- [How It Works](HOW_IT_WORKS.md) - translation pipeline
- [AI Guidelines](AI_GUIDELINES.md) - AI development practices
- [Phase 14](phases/PHASE-14-anthropic-claude-translation.md) - Claude integration

---

## 🔍 Finding Information

### Common Questions

**Q: How do I deploy to production?**
→ [Deployment Guide](DEPLOYMENT.md)

**Q: What are all the environment variables?**
→ [Environment Variables](ENVIRONMENT.md)

**Q: How does article translation work?**
→ [How It Works](HOW_IT_WORKS.md)

**Q: What's the database structure?**
→ [Database Schema](DATABASE.md)

**Q: How much does it cost to run?**
→ [Technical Documentation](TECHNICAL.md) - Cost Estimation section

**Q: Why was X feature implemented this way?**
→ [Development Phases](phases/README.md) - find the relevant phase

**Q: How do I troubleshoot Y error?**
→ [Troubleshooting](TROUBLESHOOTING.md)

**Q: What's the system architecture?**
→ [Architecture](ARCHITECTURE.md)

---

## 📝 Documentation Standards

### Phase Documentation
- Each major feature gets its own phase document in `phases/`
- Format: `PHASE-XX-feature-name.md`
- Include: timeline, motivation, decisions, implementation, outcomes
- See [Phase 52](phases/PHASE-52-connections-game.md) as example

### Work Logs
- Daily development activities in `work-logs/`
- Format: `YYYY-MM-DD-topic.md`
- Purpose: AI context preservation, detailed change tracking
- See [work-logs/README.md](work-logs/README.md) for template

### Code Documentation
- Inline comments for complex logic
- Docstrings for functions/classes
- README files in each major directory

---

## 🔄 Keeping Documentation Updated

When making changes:

1. **New Feature/Phase**:
   - Create `phases/PHASE-XX-feature-name.md`
   - Update `phases/README.md` index
   - Update relevant technical docs

2. **Architecture Change**:
   - Update [Architecture](ARCHITECTURE.md)
   - Update [How It Works](HOW_IT_WORKS.md) if workflow changes
   - Create phase document explaining decision

3. **New API Endpoint**:
   - Update [API Reference](API.md)
   - Update [Database Schema](DATABASE.md) if data model changes

4. **New Environment Variable**:
   - Update [Environment Variables](ENVIRONMENT.md)
   - Update [Deployment Guide](DEPLOYMENT.md) if deployment process changes

5. **Infrastructure Change**:
   - Update [Architecture](ARCHITECTURE.md)
   - Update [Deployment Guide](DEPLOYMENT.md)
   - Update [Technical Documentation](TECHNICAL.md) if costs/performance affected

---

## 📊 Documentation Statistics

- **Total Phases**: 52 (as of 2025-12-31)
- **Total Documentation Files**: 60+
- **Lines of Documentation**: ~10,000+
- **Last Major Reorganization**: 2025-12-31 (Phase 53 - Documentation restructure)

---

**For questions or documentation issues:**
- Open an issue in the repository
- Contact: dev@sedaily.com

---

*This documentation is maintained by the Seoul Economic Digital Development Team and updated with each phase.*
