import uk.ltd.filmlight.flapi.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

class OpenScene {

    public static void main( String[] args )
    {
        Connection conn = null;
        String host = "localhost";
        String dbpath = null;

        for( int i = 0; i < args.length; ++i )
        {
            if( args[i].equals("-h") )
            {
                if( i < (args.length-1) )
                {
                    host = args[++i];
                }
                else
                {
                    System.out.printf( "No hostname specified for -h argument\n" );
                    System.exit(1);
                }
            }
            else if( dbpath == null )
            {
                dbpath = args[i];
            }
        }

        if( dbpath == null )
        {
            System.out.printf( "No database host:job specified\n" );
            System.exit(1);
        }
            
        try
        {
            conn = new Connection(host);
            conn.connect();

            System.out.printf( "Opening %s", dbpath );
            
            ScenePath sp = conn.Scene.parsePath( dbpath );
            
            HashSet<String> flags = new HashSet<String>();
            flags.add( Constants.OPENFLAG_READ_ONLY );
            
            Scene s = conn.Scene.openScene( sp, flags );
            
            System.out.printf("\n");
            System.out.flush();

            s.closeScene();
        }
        catch( FLAPIException ex )
        {
            System.out.printf( "Error: %s\n", ex.getMessage() );
            System.exit(1);
        }
        finally
        {
            if( conn != null )
                conn.close();
        }
    }
}
