import React from 'react';
import { Shield, Menu, X, LogOut } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

interface NavbarProps {
}

export const Navbar: React.FC<NavbarProps> = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = React.useState(false);

  const isHomePage = location.pathname === '/';

  return (
    <nav className="bg-cyber-darker border-b border-cyber-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="relative">
              <Shield className="w-8 h-8 text-risk-critical" />
              <div className="absolute inset-0 bg-risk-critical/20 blur-lg group-hover:blur-xl transition-all" />
            </div>
            <span className="font-bold text-xl text-white">FraudShield AI</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            {!isHomePage && (
              <>
                <Link
                  to="/scan"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Analyze
                </Link>
                <button
                  onClick={() => navigate('/')}
                  className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Home
                </button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-gray-300 hover:text-white"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {!isHomePage && (
              <>
                <Link
                  to="/scan"
                  className="block px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  Analyze
                </Link>
                <button
                  onClick={() => navigate('/')}
                  className="w-full text-left px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  Home
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};
