import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { ApiError } from "../lib/errors";
import { apiGet } from "../lib/apiClient";

interface ConversionItem {
  id: number;
  task_id: string;
  status: string;
  output_path?: string;
  thumbnail_url?: string;
  created_at?: string;
}

const HistoryView: React.FC = () => {
  const [history, setHistory] = useState<ConversionItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        console.log("Fetching history with token:", token ? "Present" : "Missing");
        const data = await apiGet<ConversionItem[]>("history", {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        setHistory(data);
      } catch (err) {
        console.error("Error fetching history:", err);
        if (err instanceof ApiError && err.code === "UNAUTHORIZED") {
          navigate("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load history");
      }
    };
    fetchHistory();
  }, [token, navigate]);

  return (
    <div className="history-view p-4 md:p-6 text-sm md:text-base">
      {error && <p className="error mb-4">{error}</p>}

      {/* Card view for mobile */}
      <div className="md:hidden space-y-4">
        {history.map(item => (
          <div key={item.task_id} className="bg-white shadow rounded-lg p-4">
            {item.thumbnail_url && (
              <img
                src={item.thumbnail_url}
                alt={item.task_id}
                className="mb-2 w-24 h-auto"
              />
            )}
            <div className="flex justify-between mb-2">
              <span className="font-medium">{item.status}</span>
              <span>{item.created_at ? new Date(item.created_at).toLocaleString() : "-"}</span>
            </div>
            {item.output_path && (
              <div className="flex space-x-4">
                <a href={item.output_path} download>
                  Descargar
                </a>
                <a href={item.output_path} target="_blank" rel="noopener noreferrer">
                  Ver
                </a>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Table view for desktop */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="text-left">
              <th className="p-2 md:p-4">Miniatura</th>
              <th className="p-2 md:p-4">Estado</th>
              <th className="p-2 md:p-4">Fecha</th>
              <th className="p-2 md:p-4">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {history.map(item => (
              <tr key={item.task_id} className="border-t">
                <td className="p-2 md:p-4">
                  {item.thumbnail_url && (
                    <img src={item.thumbnail_url} alt={item.task_id} width={60} />
                  )}
                </td>
                <td className="p-2 md:p-4">{item.status}</td>
                <td className="p-2 md:p-4">{item.created_at ? new Date(item.created_at).toLocaleString() : "-"}</td>
                <td className="p-2 md:p-4">
                  {item.output_path && (
                    <>
                      <a href={item.output_path} download>
                        Descargar
                      </a>{" "}
                      <a href={item.output_path} target="_blank" rel="noopener noreferrer">
                        Ver
                      </a>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryView;
