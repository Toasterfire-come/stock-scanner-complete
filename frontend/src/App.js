import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import StockDashboard from './components/StockDashboard';
import Login from './components/Login';
import Register from './components/Register';
import Header from './components/Header';
import { Loader2 } from 'lucide-react';
import './App.css';

// Protected Route component
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                    <div className="text-gray-600">Loading...</div>
                </div>
            </div>
        );
    }
    
    return isAuthenticated ? children : <AuthPage />;
};

// Public Route component (redirects to dashboard if authenticated)
const PublicRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
                    <div className="text-gray-600">Loading...</div>
                </div>
            </div>
        );
    }
    
    return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
};

// Auth page with login/register toggle
const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    
    return isLogin ? 
        <Login onToggleMode={() => setIsLogin(false)} /> : 
        <Register onToggleMode={() => setIsLogin(true)} />;
};

// Main App Layout
const AppLayout = ({ children }) => {
    const { isAuthenticated } = useAuth();
    
    return (
        <div className="min-h-screen bg-gray-50">
            {isAuthenticated && <Header />}
            {children}
        </div>
    );
};

// App component
const App = () => {
    return (
        <AuthProvider>
            <BrowserRouter>
                <AppLayout>
                    <Routes>
                        {/* Public routes */}
                        <Route 
                            path="/auth" 
                            element={
                                <PublicRoute>
                                    <AuthPage />
                                </PublicRoute>
                            } 
                        />
                        
                        {/* Protected routes */}
                        <Route 
                            path="/dashboard" 
                            element={
                                <ProtectedRoute>
                                    <StockDashboard />
                                </ProtectedRoute>
                            } 
                        />
                        
                        {/* Default redirect */}
                        <Route 
                            path="/" 
                            element={<Navigate to="/dashboard" replace />} 
                        />
                        
                        {/* Catch all - redirect to dashboard */}
                        <Route 
                            path="*" 
                            element={<Navigate to="/dashboard" replace />} 
                        />
                    </Routes>
                </AppLayout>
            </BrowserRouter>
        </AuthProvider>
    );
};

export default App;