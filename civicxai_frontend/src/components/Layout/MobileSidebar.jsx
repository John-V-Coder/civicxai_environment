import React from 'react';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import Sidebar from './Sidebar';

const MobileSidebar = ({ open, onOpenChange }) => {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-64 p-0">
        <Sidebar />
      </SheetContent>
    </Sheet>
  );
};

export default MobileSidebar;
