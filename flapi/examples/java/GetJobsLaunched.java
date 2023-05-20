import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class GetJobsLaunched {

    public static void main( String[] args )
    {
        Connection conn;
        String dbhost = "localhost";

        for( int i = 0; i < args.length; ++i )
        {
            if( args[i].equals("-db") )
            {
                if( i < (args.length-1) )
                {
                    dbhost = args[++i];
                }
                else
                {
                    System.out.printf( "No database hostname specified for -db argument\n" );
                    System.exit(1);
                }
            }
        }

        try
        {
            conn = new Connection();
            conn.launch();
            
            ArrayList<String> jobs = conn.JobManager.getJobs(dbhost);
            for( String j : jobs )
                System.out.printf( String.format( "Found job %s:%s\n", "localhost", j ) );
        
            conn.close();
        }
        catch( FLAPIException ex )
        {
            System.out.printf( "Error: %s\n", ex.getMessage() );
            System.out.println("FAIL");
            System.exit(1);
        }

        System.out.println("PASS");
    }
}
