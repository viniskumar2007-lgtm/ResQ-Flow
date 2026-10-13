import { useEffect, useState } from "react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import { Link } from "react-router-dom";
import L from "leaflet";
import { apiRequest } from "../services/api";
import "leaflet/dist/leaflet.css";

const createIcon = (severity) => {
  const colors = {
    CRITICAL: "#dc2626",
    HIGH: "#ea580c",
    MEDIUM: "#ca8a04",
    LOW: "#16a34a",
  };

  const color = colors[String(severity || "").toUpperCase()] || "#2563eb";

  return L.divIcon({
    className: "resq-map-marker",
    html: `
      <div
        style="
          width: 18px;
          height: 18px;
          background: ${color};
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        "
      ></div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
};

const FitMapToIncidents = ({ incidents }) => {
  const map = useMap();

  useEffect(() => {
    if (!incidents.length) return;

    const bounds = incidents.map((incident) => [
      Number(incident.latitude),
      Number(incident.longitude),
    ]);

    map.fitBounds(bounds, {
      padding: [50, 50],
      maxZoom: 12,
    });
  }, [incidents, map]);

  return null;
};

const RescueMap = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchIncidents = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest("/api/incidents");

      const incidentList = Array.isArray(data)
        ? data
        : data.incidents || [];

      setIncidents(incidentList);
    } catch (err) {
      setError(err.message || "Failed to load incidents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const mappedIncidents = incidents.filter(
    (incident) =>
      incident.latitude != null &&
      incident.longitude != null &&
      !Number.isNaN(Number(incident.latitude)) &&
      !Number.isNaN(Number(incident.longitude))
  );

  const criticalCount = mappedIncidents.filter(
    (incident) =>
      String(incident.severity).toUpperCase() === "CRITICAL"
  ).length;

  const highCount = mappedIncidents.filter(
    (incident) =>
      String(incident.severity).toUpperCase() === "HIGH"
  ).length;

  return (
    <div className="rescue-map-page">
      <section className="map-page-header">
        <div>
          <Link to="/dashboard" className="back-link">
            ← Back to Dashboard
          </Link>

          <h2>Rescue Map</h2>

          <p>
            Monitor emergency locations and coordinate rescue
            operations.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchIncidents}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </section>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <section className="map-summary">
        <div className="map-summary-card">
          <span>Total Located</span>
          <strong>{mappedIncidents.length}</strong>
        </div>

        <div className="map-summary-card critical-summary">
          <span>Critical</span>
          <strong>{criticalCount}</strong>
        </div>

        <div className="map-summary-card high-summary">
          <span>High</span>
          <strong>{highCount}</strong>
        </div>
      </section>

      <section className="map-card">
        <div className="map-card-header">
          <div>
            <h3>Emergency Locations</h3>
            <p>
              {mappedIncidents.length} incident
              {mappedIncidents.length !== 1 ? "s" : ""} shown
              on the map.
            </p>
          </div>

          <div className="map-legend">
            <span>
              <i className="legend-dot critical-dot"></i>
              Critical
            </span>

            <span>
              <i className="legend-dot high-dot"></i>
              High
            </span>

            <span>
              <i className="legend-dot medium-dot"></i>
              Medium
            </span>

            <span>
              <i className="legend-dot low-dot"></i>
              Low
            </span>
          </div>
        </div>

        <div className="map-container">
          {mappedIncidents.length === 0 && !loading ? (
            <div className="map-empty">
              <div>⌖</div>
              <h3>No mapped incidents</h3>
              <p>
                No incidents currently contain valid location
                coordinates.
              </p>
            </div>
          ) : (
            <MapContainer
              center={[20.5937, 78.9629]}
              zoom={5}
              scrollWheelZoom={true}
              style={{
                height: "100%",
                width: "100%",
              }}
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <FitMapToIncidents
                incidents={mappedIncidents}
              />

              {mappedIncidents.map((incident) => (
                <Marker
                  key={incident.id}
                  position={[
                    Number(incident.latitude),
                    Number(incident.longitude),
                  ]}
                  icon={createIcon(incident.severity)}
                >
                  <Popup>
                    <div style={{ minWidth: "180px" }}>
                      <strong>
                        {incident.disaster_type ||
                          "Emergency Incident"}
                      </strong>

                      <hr />

                      <div>
                        <b>Incident:</b> #{incident.id}
                      </div>

                      <div>
                        <b>Severity:</b>{" "}
                        {incident.severity || "Unknown"}
                      </div>

                      <div>
                        <b>Status:</b>{" "}
                        {incident.status || "Unknown"}
                      </div>

                      <div>
                        <b>Priority:</b>{" "}
                        {incident.priority_score ?? "N/A"}
                      </div>

                      <div style={{ marginTop: "10px" }}>
                        <Link
                          to={`/incidents/${incident.id}`}
                          className="map-popup-link"
                        >
                          View Incident Details →
                        </Link>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          )}
        </div>
      </section>
    </div>
  );
};

export default RescueMap;
