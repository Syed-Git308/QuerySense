import React, { useEffect, useRef } from 'react';
import { User, Settings, LogOut } from 'lucide-react';

interface ProfileDropdownProps {
  onClose: () => void;
}

const ProfileDropdown: React.FC<ProfileDropdownProps> = ({ onClose }) => {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const menuItems = [
    { icon: User, label: 'Profile', onClick: () => console.log('Profile clicked') },
    { icon: Settings, label: 'Settings', onClick: () => console.log('Settings clicked') },
    { icon: LogOut, label: 'Logout', onClick: () => console.log('Logout clicked') },
  ];

  return (
    <div
      ref={dropdownRef}
      className="absolute right-0 top-10 w-44 bg-white/90 backdrop-blur-xl rounded-xl shadow-lg border border-black/10 py-1 animate-in slide-in-from-top-2 duration-200"
    >
      {menuItems.map((item, index) => (
        <button
          key={index}
          onClick={item.onClick}
          className="w-full px-3 py-2 text-left flex items-center space-x-3 text-black/80 hover:bg-black/5 transition-all duration-150 mx-1 rounded-lg"
        >
          <item.icon size={14} strokeWidth={1.5} className="text-black/60" />
          <span className="text-sm font-medium">{item.label}</span>
        </button>
      ))}
    </div>
  );
};

export default ProfileDropdown;