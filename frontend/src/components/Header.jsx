import React, { useState } from 'react';
import { useAuth } from '../context/EnhancedAuthContext';
import { Card, CardContent } from './ui/card';
import { User, LogOut, Settings, Wallet } from 'lucide-react';

const Header = () => {
    const { user, logout } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);

    if (!user) return null;

    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <h1 className="text-xl font-bold text-gray-900">Stock Scanner</h1>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Plan Badge */}
                        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                            user.plan === 'free' ? 'bg-gray-100 text-gray-800' :
                            user.plan === 'bronze' ? 'bg-orange-100 text-orange-800' :
                            user.plan === 'silver' ? 'bg-gray-200 text-gray-800' :
                            user.plan === 'gold' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                        }`}>
                            {user.plan.toUpperCase()} PLAN
                        </div>

                        {/* Usage Stats */}
                        <div className="text-xs text-gray-600">
                            {user.usage.daily_calls}/{user.limits.daily} daily calls
                        </div>

                        {/* User Menu */}
                        <div className="relative">
                            <button
                                onClick={() => setShowUserMenu(!showUserMenu)}
                                className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 p-2 rounded-md hover:bg-gray-100"
                            >
                                <User className="w-5 h-5" />
                                <span className="hidden sm:block">{user.first_name} {user.last_name}</span>
                            </button>

                            {showUserMenu && (
                                <div className="absolute right-0 mt-2 w-48 z-50">
                                    <Card>
                                        <CardContent className="p-0">
                                            <div className="py-1">
                                                <div className="px-4 py-2 border-b">
                                                    <div className="text-sm font-medium text-gray-900">
                                                        {user.first_name} {user.last_name}
                                                    </div>
                                                    <div className="text-sm text-gray-500">{user.email}</div>
                                                </div>
                                                
                                                <button className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                                    <Settings className="w-4 h-4 mr-3" />
                                                    Profile Settings
                                                </button>
                                                
                                                <button className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                                    <Wallet className="w-4 h-4 mr-3" />
                                                    Billing & Plans
                                                </button>
                                                
                                                <div className="border-t">
                                                    <button 
                                                        onClick={logout}
                                                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                                    >
                                                        <LogOut className="w-4 h-4 mr-3" />
                                                        Sign Out
                                                    </button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;