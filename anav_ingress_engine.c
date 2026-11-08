#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sqlite3.h>

#define DB_PATH "anav_ledger.db"

void log_ingress_event(const char *proof, const char *payload) {
    sqlite3 *db;
    char *err_msg = 0;
    int rc = sqlite3_open(DB_PATH, &db);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "[C-ENGINE ERROR] Cannot open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return;
    }

    const char *sql = "CREATE TABLE IF NOT EXISTS global_ingress_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, proof TEXT, payload TEXT, amount_usdc REAL DEFAULT 0.0, bridged INTEGER DEFAULT 1);";
    rc = sqlite3_exec(db, sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "[C-ENGINE ERROR] SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    char query[1024];
    snprintf(query, sizeof(query), "INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (%f, '%s', '%s', 0.0, 1);", 
             (double)time(NULL), proof, payload);

    rc = sqlite3_exec(db, query, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "[C-ENGINE ERROR] Insert failed: %s\n", err_msg);
        sqlite3_free(err_msg);
    } else {
        printf("[C-ENGINE SUCCESS] Ingress proof and payload committed at high speed.\n");
    }

    sqlite3_close(db);
}

int main(int argc, char *argv[]) {
    printf("============================================================\n");
    printf(" PROJECT ANAV // C-BASED HIGH-PERFORMANCE INGRESS ENGINE\n");
    printf("============================================================\n");
    
    const char *proof = (argc > 1) ? argv[1] : "c_engine_default_proof_01";
    const char *payload = (argc > 2) ? argv[2] : "{\"engine\": \"native_c\", \"status\": \"optimized\"}";
    
    log_ingress_event(proof, payload);
    return 0;
}
