#!/bin/bash

echo "🚀 Starting AI Teacher Chatbot..."
echo ""

# Kill any existing processes
pkill -f "uvicorn backend.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend in background
cd /home/evocenta/PycharmProjects/AI_teacher

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/#.*//')
    set +a
fi

# Ensure OPENAI_API_BASE is unset
unset OPENAI_API_BASE

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not found in .env file"
    exit 1
fi

# Start backend
pipenv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend starting (PID: $BACKEND_PID)..."

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check backend.log for details:"
        tail -10 backend.log
        exit 1
    fi
    sleep 1
done

# Start frontend in background
cd /home/evocenta/PycharmProjects/AI_teacher/frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend starting (PID: $FRONTEND_PID)..."

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:4200 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start. Check frontend/frontend.log for details:"
        tail -10 frontend.log
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 Both servers are running successfully!"
echo ""
echo "📍 Frontend UI: http://localhost:4200"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /home/evocenta/PycharmProjects/AI_teacher/backend.log"
echo "   Frontend: tail -f /home/evocenta/PycharmProjects/AI_teacher/frontend/frontend.log"
echo ""
echo "🛑 To stop: pkill -f 'uvicorn backend.main:app' && pkill -f vite"
echo ""
echo "✨ Open http://localhost:4200 in your browser!"
