package com.flconv.app

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import java.io.FileOutputStream

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        setContent {
            MaterialTheme {
                ConverterUI()
            }
        }
    }
}

@Composable
fun ConverterUI() {
    val context = LocalContext.current
    var statusText by remember { mutableStateOf("Select an .flp file to convert") }
    var isLoading by remember { mutableStateOf(false) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        isLoading = true
        statusText = "Converting..."

        val flpFile = File(context.cacheDir, "input.flp")
        val flmFile = File(context.cacheDir, "output.flm")
        
        try {
            context.contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(flpFile).use { output ->
                    input.copyTo(output)
                }
            }
            
            val py = Python.getInstance()
            val pyObj = py.getModule("converter")
            val result = pyObj.callAttr("convert", flpFile.absolutePath, flmFile.absolutePath).toString()
            
            if (result == "Success") {
                statusText = "Conversion Successful! Sharing file..."
                shareFile(context, flmFile)
            } else {
                statusText = "Error: $result"
            }
        } catch (e: Exception) {
            statusText = "Failed: ${e.message}"
        } finally {
            isLoading = false
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("FL Studio PC to Mobile", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        Text("Converts .flp to .flm directly on your phone.", style = MaterialTheme.typography.bodyMedium)
        Spacer(modifier = Modifier.height(32.dp))

        if (isLoading) {
            CircularProgressIndicator()
        } else {
            Button(
                onClick = { filePicker.launch("*/*") },
                modifier = Modifier.fillMaxWidth().height(56.dp)
            ) {
                Text("Select .flp File")
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = statusText, 
            color = if (statusText.startsWith("Error") || statusText.startsWith("Failed")) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
        )
    }
}

fun shareFile(context: Context, file: File) {
    val uri = androidx.core.content.FileProvider.getUriForFile(
        context,
        "${context.packageName}.provider",
        file
    )
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "application/octet-stream"
        putExtra(Intent.EXTRA_STREAM, uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(intent, "Share FLM File"))
}
