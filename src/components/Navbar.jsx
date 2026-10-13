import { useAuth } from "../context/AuthContext";

const Navbar = () => {
  const { user } = useAuth();

  return (
    <header className="topbar">
      <div>
        <h1>Emergency Operations</h1>
        <p>Monitor and coordinate active rescue incidents</p>
      </div>

      <div className="topbar-user">
        <div className="user-avatar">
          {(user?.username || user?.name || "R").charAt(0).toUpperCase()}
        </div>

        <div>
          <strong>{user?.username || user?.name || "Rescuer"}</strong>
          <span>{user?.role || "Rescue Operator"}</span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;