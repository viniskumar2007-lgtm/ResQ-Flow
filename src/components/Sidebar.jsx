import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Sidebar = () => {
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">R</div>

        <div>
          <h2>ResQ-Flow</h2>
          <span>Rescue Command Center</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span>▣</span>
          Dashboard
        </NavLink>

        <NavLink
          to="/incidents"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span>⚠</span>
          Incidents
        </NavLink>

        <NavLink
          to="/map"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span>⌖</span>
          Rescue Map
        </NavLink>
      </nav>

      <div className="sidebar-bottom">
        <button className="logout-button" onClick={logout}>
          <span>↪</span>
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;