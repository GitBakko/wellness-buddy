// App shell — placeholder root. Plans 03/04/06/07 hang real chrome
// (NavigationShell + AppBar + BottomTabBar + ErrorBoundary) off this.
import { Outlet } from 'react-router';

export default function App() {
  return <Outlet />;
}
