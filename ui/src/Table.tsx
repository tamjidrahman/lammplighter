import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TablePagination, IconButton, Typography, CircularProgress } from '@mui/material';
import GetAppIcon from '@mui/icons-material/GetApp';

export interface InputConfig {
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

const instance = axios.create({ baseURL: process.env.REACT_APP_API_URL });

const MyTable: React.FC = () => {
    const [data, setData] = useState<TableRowData[]>([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [loading, setLoading] = useState(false);
    const [refreshTimer, setRefreshTimer] = useState(0);

    const fetchData = () => {
        setLoading(true);
        instance.get("runs")
            .then((response) => {
                setData(response.data);
                setLoading(false);
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
                setLoading(false);
            });
    };

    useEffect(() => {

        const intervalId = setInterval(() => {
            if (refreshTimer <= 0) {
                fetchData();
                console.log(refreshTimer)
                setRefreshTimer(100);
            } else {
                console.log(refreshTimer)
                setRefreshTimer(refreshTimer - 1);
            }
        }, 100);

        return () => {
            clearInterval(intervalId);
        };
    }, [refreshTimer]);

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
        <div
            style={{
                padding: '20px',
                border: '1px solid #e0e0e0',
                borderRadius: '5px',
                position: 'relative',
            }}
        >
            <Typography variant="h5" style={{ marginBottom: '20px' }}>
                Runs
            </Typography>
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    width: '40px',
                    height: '40px',
                    zIndex: 1,
                }}
            >
                {loading ? (
                    <CircularProgress variant='determinate' size={40} thickness={4} value={100 - (refreshTimer)} />
                ) : (
                    <CircularProgress
                        variant='determinate'
                        size={40}
                        thickness={4}
                        value={100 - (refreshTimer)}
                    />
                )}
            </div>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>RunID</TableCell>
                            <TableCell>InputName</TableCell>
                            <TableCell>Commands</TableCell>
                            <TableCell>Status</TableCell>
                            {/* Add more table headers as needed */}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {slicedData.map((row) => (
                            <TableRow key={row.run.id}>
                                <TableCell>{row.run.id}</TableCell>
                                <TableCell>{row.inputconfig.name}</TableCell>
                                <TableCell>{row.run.commands.join(', ')}</TableCell>
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
                                        row.run.status // Display the status as is
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
