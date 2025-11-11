
import { Metadata } from 'next';
import EnhancedRWADashboard from '@/components/rwa/enhanced-rwa-dashboard';

export const metadata: Metadata = {
  title: 'Oracle RWA Engine | Sovereign Legacy Loop',
  description: 'Real-World Asset management inspired by Larry Ellison\'s $393B wealth strategy',
};

export default function RWAPage() {
  return (
    <div className="container mx-auto p-6 space-y-8">
      <EnhancedRWADashboard />
    </div>
  );
}
