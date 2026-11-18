import api from "../services/api";
import type Telemetry from "../types/telemetry";

export async function getTelemetryHistory(
    machineId: string,
): Promise<Telemetry[]> {
    const response = await api.get<Telemetry[]>(
        `/telemetry/history/${machineId}`
    );

    return response.data;
}

export async function getLatestTelemetry(): Promise<Telemetry> {
    const response = await api.get<Telemetry>(
        "/telemetry/latest"
    );

    return response.data;
}
