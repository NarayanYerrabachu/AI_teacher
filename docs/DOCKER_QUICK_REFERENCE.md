# Docker Quick Reference

**AI Teacher Project - Docker Commands Cheat Sheet**

## Essential Commands

### Build & Start
```bash
make build          # Build all images
make up             # Start services
make down           # Stop services
make restart        # Restart services
```

### Monitoring
```bash
make logs           # View all logs
make logs-backend   # Backend logs only
make ps             # Show running containers
make stats          # Resource usage
```

### Maintenance
```bash
make clean          # Remove containers/images
make backup         # Backup data volumes
make shell-backend  # Access backend shell
```

## Build Optimizations Summary

### Performance Improvements
- **First Build**: 15-20 minutes (was 100+ minutes)
- **Cached Build**: 2-5 minutes
- **PyTorch**: 90 seconds (was 10+ minutes)

### Key Changes
1. ✅ CPU-only PyTorch (184 MB vs 2.5+ GB)
2. ✅ Removed BuildKit dependency
3. ✅ Suppressed pip root warnings
4. ✅ Improved layer caching

### Image Sizes
- PyTorch: 184 MB (93% smaller)
- Build Context: 5 MB (97% smaller)
- Final Image: ~2.5 GB (37% smaller)

## Troubleshooting

### Build Too Slow?
```bash
# Clear cache and rebuild
docker builder prune -a
make rebuild
```

### Out of Space?
```bash
# Clean up
docker system prune -a --volumes
docker image prune -a
```

### Can't Connect?
```bash
# Check health
curl http://localhost:8000/health
curl http://localhost:4200/

# View logs
make logs-backend
```

### Module Not Found?
```bash
# Rebuild without cache
make rebuild
```

## Build Status Monitoring

### Watch Build Progress
```bash
# Real-time monitoring
docker compose build backend 2>&1 | tee build.log

# Check progress
tail -f build.log
```

### Expected Build Stages
```
Stage 1: System deps        (~30 sec)
Stage 2: Pip + pipenv        (~10 sec)
Stage 3: PyTorch CPU         (~90 sec) ⚡
Stage 4: Other deps          (~10-15 min)
Stage 5: Production image    (~30 sec)
Total: 15-20 minutes first time
```

## Access Points

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Common Workflows

### Adding Dependencies
```bash
pipenv install new-package
docker compose build backend
make restart
```

### Code Changes
```bash
# Make changes...
make down
make build  # Fast with caching!
make up
```

### View Database
```bash
make shell-backend
ls -la /app/chroma_db
```

---

**Full Documentation**: See `docs/DOCKER_BUILD_OPTIMIZATION.md`
