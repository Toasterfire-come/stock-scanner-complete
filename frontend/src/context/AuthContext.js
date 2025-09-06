import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const BASE_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('rts_token');
        const userData = localStorage.getItem('user_data');

        if (token && userData) {
            setUser(JSON.parse(userData));
        }
        setLoading(false);
    }, []);

    const login = async (credentials) => {
        const response = await fetch(`${BASE_URL}/api/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });

        const data = await response.json();

        if (data.success) {
            localStorage.setItem('rts_token', data.data.api_token);
            localStorage.setItem('user_data', JSON.stringify(data.data));
            setUser(data.data);
            return data.data;
        }

        throw new Error(data.error);
    };

    const register = async (userData) => {
        const response = await fetch(`${BASE_URL}/api/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: userData.username,
                email: userData.email,
                password: userData.password,
                first_name: userData.firstName,
                last_name: userData.lastName
            })
        });

        const data = await response.json();

        if (data.success) {
            localStorage.setItem('rts_token', data.data.api_token);
            localStorage.setItem('user_data', JSON.stringify(data.data));
            setUser(data.data);
            return data.data;
        }

        throw new Error(data.error);
    };

    const logout = () => {
        localStorage.removeItem('rts_token');
        localStorage.removeItem('user_data');
        setUser(null);
    };

    const getAuthHeaders = () => {
        const token = localStorage.getItem('rts_token');
        return {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
    };

    const value = {
        user,
        login,
        register,
        logout,
        getAuthHeaders,
        isAuthenticated: !!user,
        loading
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};