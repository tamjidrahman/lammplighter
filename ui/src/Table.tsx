import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

interface InputConfig {
    id: number;
    name: string;
    s3_path: string;
    // Add more fields as needed
}

interface Run {
    id: number;
    input_id: string;
    commands: string[];
    status: string;
    // Add more fields as needed
}

interface TableRowData {
    run: Run;
    inputconfig: InputConfig;
    // Add more fields as needed
}
const instance = axios.create({ baseURL: 'http://localhost:80' })

const MyTable: React.FC = () => {
    const [data, setData] = useState<TableRowData[]>([]);

    useEffect(() => {
        // Replace 'YOUR_API_ENDPOINT' with the actual REST API endpoint
        instance.get("runs")
            .then((response) => {
                setData(response.data);
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
            });
    }, []);

    console.log(data)

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>RunID</TableCell>
                        <TableCell>InputName</TableCell>
                        <TableCell>Commands</TableCell>
                        {/* Add more table headers as needed */}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.map((row) => (
                        <TableRow key={row.run.id}>
                            <TableCell>{row.run.id}</TableCell>
                            <TableCell>{row.inputconfig.name}</TableCell>
                            <TableCell>{row.run.commands}</TableCell>
                            {/* Add more table cells as needed */}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default MyTable;
