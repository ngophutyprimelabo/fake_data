-- Count users with and without personnel records
SELECT 
    'Users with personnel' AS user_type,
    COUNT(*) AS count
FROM 
    users u
INNER JOIN 
    personnels p ON u.username = p.external_username

UNION ALL

SELECT 
    'Users without personnel' AS user_type,
    COUNT(*) AS count
FROM 
    users u
LEFT JOIN 
    personnels p ON u.username = p.external_username
WHERE 
    p.id IS NULL;