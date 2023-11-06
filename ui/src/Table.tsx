import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TablePagination, IconButton } from '@mui/material';
import GetAppIcon from '@mui/icons-material/GetApp';

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

const instance = axios.create({ baseURL: process.env.REACT_APP_API_URL })

const MyTable: React.FC = () => {
    const [data, setData] = useState<TableRowData[]>([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

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

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const downloadables = (runId: number) => {
        // Call the API with the run ID as a parameter
        instance.get("outputs", {
            params: {
                run_id: runId
            }
        })
            .then((response) => {
                // Implement the logic to determine downloadable files
                return response.data; // Assuming response.data contains downloadable files
            })
            .catch((error) => {
                console.error('Error determining downloadable files:', error);
                return []; // Return an empty array if there's an error
            });
    };

    const slicedData = data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

    return (
        <div>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>RunID</TableCell>
                            <TableCell>InputName</TableCell>
                            <TableCell>Commands</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Downloadable Files</TableCell>
                            {/* Add more table headers as needed */}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {slicedData.map((row) => (
                            <TableRow key={row.run.id}>
                                <TableCell>{row.run.id}</TableCell>
                                <TableCell>{row.inputconfig.name}</TableCell>
                                <TableCell>{row.run.commands.join(', ')}</TableCell>
                                <TableCell>{row.run.status}</TableCell>
                                <TableCell>
                                    {row.run.status === 'COMPLETE' ? (
                                        <IconButton
                                            size="small"
                                            color="primary"
                                            onClick={() => downloadables(row.run.id)}
                                        >
                                            <GetAppIcon />
                                        </IconButton>
                                    ) : (
                                        'N/A'
                                    )}
                                </TableCell>
                                {/* Add more table cells as needed */}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <TablePagination
                component="div"
                count={data.length}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleChangeRowsPerPage}
            />
        </div>
    );
};

export default MyTable;
